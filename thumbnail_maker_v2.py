# consumer producer by using Queue
# Download images put downloaded images into Queue (produce),
# resizer get it from Queue (consume) and do resize
# Both works as separate threads

import logging
import os
import threading
import time
from queue import Queue
from urllib.parse import urlparse
from urllib.request import urlretrieve

import PIL
from PIL import Image

logging.basicConfig(filename='logfile.log', level=logging.DEBUG)


class ThumbnailMakerService_v2(object):
    def __init__(self, home_dir='.'):
        self.home_dir = home_dir
        self.input_dir = self.home_dir + os.path.sep + 'incoming'
        self.output_dir = self.home_dir + os.path.sep + 'outgoing'
        self.queue = Queue()

    def download_image(self, url, is_last):
        img_filename = urlparse(url).path.split('/')[-1]
        urlretrieve(url, self.input_dir + os.path.sep + img_filename)
        self.queue.put(img_filename)

        # poison pill
        if is_last:
            self.queue.put(None)

    def download_images(self, img_url_list):
        # validate inputs
        if not img_url_list:
            return
        os.makedirs(self.input_dir, exist_ok=True)

        logging.info("beginning image downloads")

        start = time.perf_counter()
        cnt_url = 0
        for url in img_url_list:
            is_last = cnt_url == len(img_url_list)
            t = threading.Thread(target=self.download_image, args=(url, is_last))
            cnt_url += 1
            t.start()
        end = time.perf_counter()

        logging.info("downloaded {} images in {} seconds".format(len(img_url_list), end - start))

    def perform_resizing(self):
        os.makedirs(self.output_dir, exist_ok=True)

        logging.info("beginning image resizing")
        target_sizes = [32, 64, 200]
        num_images = len(os.listdir(self.input_dir))

        start = time.perf_counter()
        while True:
            filename = self.queue.get()
            if filename is None:
                print('finish')
                self.queue.task_done()
                break
            orig_img = Image.open(self.input_dir + os.path.sep + filename)
            for basewidth in target_sizes:
                img = orig_img
                # calculate target height of the resized image to maintain the aspect ratio
                wpercent = (basewidth / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(wpercent)))
                # perform resizing
                img = img.resize((basewidth, hsize), PIL.Image.LANCZOS)

                # save the resized image to the output dir with a modified file name
                new_filename = os.path.splitext(filename)[0] + '_' + str(basewidth) + os.path.splitext(filename)[1]
                img.save(self.output_dir + os.path.sep + new_filename)

            os.remove(self.input_dir + os.path.sep + filename)
            self.queue.task_done()
        end = time.perf_counter()

        logging.info("created {} thumbnails in {} seconds".format(num_images, end - start))

    def make_thumbnails(self, img_url_list):
        logging.info("START make_thumbnails")
        start = time.perf_counter()

        self.download_images(img_url_list)

        thread_consumer = threading.Thread(target=self.perform_resizing)
        thread_consumer.start()

        thread_consumer.join()

        end = time.perf_counter()
        logging.info("END make_thumbnails in {} seconds".format(end - start))
