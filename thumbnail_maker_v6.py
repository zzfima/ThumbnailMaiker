# consumer producer by using 2 Queues
# Download images put downloaded images into Queue (produce),
# resizer get it from Queue (consume) and do resize
# Both works as separate threads
# using Pool of processes

import logging
import multiprocessing
import os
import time
from queue import Queue
from threading import Thread
from urllib.parse import urlparse
from urllib.request import urlretrieve

import PIL
from PIL import Image

logging.basicConfig(filename='logfile.log', level=logging.DEBUG)


class ThumbnailMakerService_v6(object):
    def __init__(self, home_dir='.'):
        self.home_dir = home_dir
        self.input_dir = self.home_dir + os.path.sep + 'incoming'
        self.output_dir = self.home_dir + os.path.sep + 'outgoing'
        self.img_list = []

    def download_image(self, dl_queue):
        while not dl_queue.empty():
            try:
                url = dl_queue.get(block=False)
                img_filename = urlparse(url).path.split('/')[-1]
                urlretrieve(url, self.input_dir + os.path.sep + img_filename)
                self.img_list.append(img_filename)
                dl_queue.task_done()
            except Queue.Empty:
                print('Queue is empty')

    def resize_image(self, filename):
        os.makedirs(self.output_dir, exist_ok=True)

        logging.info("beginning image resizing")
        target_sizes = [32, 64, 200]

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

    def make_thumbnails(self, img_url_list):
        logging.info("START make_thumbnails")
        start = time.perf_counter()
        dl_queue = Queue()
        for img_url in img_url_list:
            dl_queue.put(img_url)

        num_dl_threads = 4
        for _ in range(num_dl_threads):
            t = Thread(target=self.download_image, args=(dl_queue,))
            t.start()

        dl_queue.join()

        pool = multiprocessing.Pool()
        pool.map(self.resize_image, self.img_list)

        pool.close()
        pool.join()

        end = time.perf_counter()
        logging.info("END make_thumbnails in {} seconds".format(end - start))
