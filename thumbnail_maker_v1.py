# consumer producer by using Queue

import logging
import os
import threading
import time
from datetime import datetime
from urllib.parse import urlparse
from urllib.request import urlretrieve

import PIL
from PIL import Image

logging.basicConfig(filename='logfile.log', level=logging.DEBUG)


class ThumbnailMakerService_v1(object):
    def __init__(self, home_dir='.'):
        self._home_dir = home_dir
        self._input_dir = self._home_dir + os.path.sep + 'incoming'
        self._output_dir = self._home_dir + os.path.sep + 'outgoing'
        self._downloaded_bytes = 0
        max_concurrent_downloads = 4
        self._downloads_semaphore = threading.BoundedSemaphore(max_concurrent_downloads)

    def __download_image(self, img_url):
        self._downloads_semaphore.acquire()
        try:
            print('start download image. ', threading.currentThread().ident, ' ', datetime.now().time())
            img_filename = urlparse(img_url).path.split('/')[-1]
            destination_path = self._input_dir + os.path.sep + img_filename
            urlretrieve(img_url, destination_path)
            image_size = os.path.getsize(destination_path)
            lock = threading.Lock()
            with lock:
                self._downloaded_bytes += image_size
        finally:
            self._downloads_semaphore.release()

    def __download_images(self, img_url_list):
        # validate inputs
        if not img_url_list:
            return
        os.makedirs(self._input_dir, exist_ok=True)

        logging.info("beginning image downloads")
        download_threads = []
        start = time.perf_counter()
        for url in img_url_list:
            t = threading.Thread(target=self.__download_image, args=(url,))
            t.start()
            download_threads.append(t)

        for t in download_threads:
            t.join()

        end = time.perf_counter()

        logging.info("downloaded {} images in {} seconds".format(len(img_url_list), end - start))

    def __perform_resizing(self):
        # validate inputs
        if not os.listdir(self._input_dir):
            return
        os.makedirs(self._output_dir, exist_ok=True)

        logging.info("beginning image resizing")
        target_sizes = [32, 64, 200]
        num_images = len(os.listdir(self._input_dir))

        start = time.perf_counter()
        for filename in os.listdir(self._input_dir):
            orig_img = Image.open(self._input_dir + os.path.sep + filename)
            for basewidth in target_sizes:
                img = orig_img
                # calculate target height of the resized image to maintain the aspect ratio
                wpercent = (basewidth / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(wpercent)))
                # perform resizing
                img = img.resize((basewidth, hsize), PIL.Image.LANCZOS)

                # save the resized image to the output dir with a modified file name
                new_filename = os.path.splitext(filename)[0] + '_' + str(basewidth) + os.path.splitext(filename)[1]
                img.save(self._output_dir + os.path.sep + new_filename)

            os.remove(self._input_dir + os.path.sep + filename)
        end = time.perf_counter()

        logging.info("created {} thumbnails in {} seconds".format(num_images, end - start))

    def make_thumbnails(self, img_url_list):
        logging.info("START make_thumbnails")
        start = time.perf_counter()

        self.__download_images(img_url_list)
        self.__perform_resizing()

        end = time.perf_counter()
        logging.info("Download size {} bytes".format(self._downloaded_bytes))
        logging.info("END make_thumbnails in {} seconds".format(end - start))
