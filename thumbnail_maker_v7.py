# consumer producer by using 2 Queues
# Download images put downloaded images into Queue (produce),
# resizer get it from Queue (consume) and do resize
# Both works as separate threads
# using Pool of processes
# using queue RPC

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


def perform_resizing(input_dir: str, output_dir: str, img_queue: multiprocessing.JoinableQueue):
    os.makedirs(output_dir, exist_ok=True)

    logging.info("beginning image resizing")
    target_sizes = [32, 64, 200]

    start = time.perf_counter()
    while True:
        filename = img_queue.get()
        if filename is None:
            print('finish')
            img_queue.task_done()
            break
        orig_img = Image.open(input_dir + os.path.sep + filename)
        for basewidth in target_sizes:
            img = orig_img
            # calculate target height of the resized image to maintain the aspect ratio
            wpercent = (basewidth / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            # perform resizing
            img = img.resize((basewidth, hsize), PIL.Image.LANCZOS)

            # save the resized image to the output dir with a modified file name
            new_filename = os.path.splitext(filename)[0] + '_' + str(basewidth) + os.path.splitext(filename)[1]
            img.save(output_dir + os.path.sep + new_filename)

        os.remove(input_dir + os.path.sep + filename)
        img_queue.task_done()
    end = time.perf_counter()

    logging.info("created thumbnail in {} seconds".format(end - start))


class ThumbnailMakerService_v7(object):
    def __init__(self, home_dir='.'):
        self.home_dir = home_dir
        self.input_dir = self.home_dir + os.path.sep + 'incoming'
        self.output_dir = self.home_dir + os.path.sep + 'outgoing'
        self.img_queue = multiprocessing.JoinableQueue()
        self.dl_queue = Queue()

    def download_image(self):
        while not self.dl_queue.empty():
            try:
                url = self.dl_queue.get(block=False)
                img_filename = urlparse(url).path.split('/')[-1]
                urlretrieve(url, self.input_dir + os.path.sep + img_filename)
                self.img_queue.put(img_filename)
                self.dl_queue.task_done()
            except Queue.Empty:
                print('Queue is empty')

    def make_thumbnails(self, img_url_list):
        logging.info("START make_thumbnails")
        start = time.perf_counter()

        for img_url in img_url_list:
            self.dl_queue.put(img_url)

        num_dl_threads = 4
        for _ in range(num_dl_threads):
            t = Thread(target=self.download_image)
            t.start()

        t2 = multiprocessing.Process(target=perform_resizing,
                                     args=(self.input_dir, self.output_dir, self.img_queue,))
        t2.start()

        self.dl_queue.join()
        self.img_queue.put(None)
        t2.join()

        end = time.perf_counter()
        logging.info("END make_thumbnails in {} seconds".format(end - start))
