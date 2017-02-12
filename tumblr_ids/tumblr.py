#!/usr/bin/env python
# -*-coding:utf-8-*-
"""
tumblr.py.

#=============================================================================
# FileName:     tumblr.py
# Desc:         download imgs from tumblr
# Author:       leyle
# Email:        leyle@leyle.com
# HomePage:     http://www.leyle.com/
# Git_page:     https://github.com/leyle
# Version:      0.1.2
# LastChange:   2015-01-22 17:26:08
#=============================================================================
    download imgs from tumblr.
    json url like: http://er0.tumblr.com/api/read/json?start=0&num=10
"""
# -*-coding:utf-8-*-
import os
import re
import threading
try:
    from queue import Queue  # py3
except ImportError:
    from Queue import Queue  # py2

from . import utils
from .mylogger import get_logger


def get_video_url(data):
    """get video url from data."""
    urls = [x.split('\\"')[0].replace('\\/', '/')
            for x in data.split('<source src=\\"') if x.startswith('http')]
    return list(set(urls))


def get_filename(url, default_vid_ext='.mp4'):
    """get filename from url."""
    if '/video_file/' in url:
        basename = url.split('/video_file/')[1].split('/')[1]
        bn_parts = list(os.path.splitext(basename))

        # set default vid ext
        if bn_parts[1] == '':
            bn_parts[1] = default_vid_ext

        return ''.join(bn_parts)
    else:
        return str(url.split('/')[-1])


class Tumblr(object):
    """tumblr class."""

    def __init__(self, blog, limit_start=0, num=30, threads_num=10, need_save=True, save_path=None,
                 img_re=None, total_post_re=None, max_posts=None, proxies=None, stream=True,
                 timeout=10, tags=['']):
        """init func."""
        self.blog = blog
        self.tags = tags
        self.tag = ''
        self.base_url = "http://%s.tumblr.com/api/read/json?start=" % self.blog
        self.total_post_re = \
            total_post_re if total_post_re else re.compile(r'"posts-total":"*(\d+)"*,')
        self.img_re = img_re if img_re else re.compile(r'photo-url-1280":"(http.*?)",')
        self.total_posts = 0
        self.max_posts = max_posts
        self.limit_start = limit_start
        self.num = num
        # limit image
        self.image_limit = None
        self.need_save = need_save
        self.stream = stream
        self.timeout = timeout
        if self.need_save:
            self.save_path = save_path
            self._check_save_path()
            self.imglog = None
        else:
            self.save_path = None
            self.imglog = get_logger("imgurl")

        self.proxies = proxies
        self.img_queue = Queue()
        self.post_queue = Queue()
        self.threads_num = threads_num

    def run(self, use_threading=True, stream=True, timeout=10, proxies=None, image_limit=None):
        """Run the downloader.

        :param image_limit: limit the download image.
        """
        # limit the Queue size
        if image_limit is not None:
            self.image_limit = image_limit
        self.proxies = proxies
        self.stream = stream
        self.timeout = timeout
        if use_threading:
            print("Started blog rip using Threads...\n")
            self.get_imgs_using_threading()
        else:
            print("Started blog rip not using Threads...\n")
            self.get_imgs()

    def _process_tags(self, total_posts_func):
        """process tags.

        Args:
            total_posts_func: Function to run when total posts valid.
        """
        for tag in self.tags:
            self.tag = tag
            print("Tag: {}".format(self.tag))
            if not self.total_posts:
                self.total_posts = self._get_total_posts()
            if self.total_posts:
                total_posts_func()
            self.total_posts = 0

    def get_imgs(self):
        """get img."""
        self._process_tags(total_posts_func=self._get_img_urls)
        if self.need_save and not self.img_queue.empty():
            self._download_imgs()

    def _process_img_queue(self, consumer):
        """process image queue.

        it is created to simplify get_imgs_using_threading func.
        """
        while True:
            if not self.img_queue.empty():
                for i in range(0, self.threads_num):
                    c = threading.Thread(target=self._download_imgs)
                    consumer.append(c)

                for i in range(0, self.threads_num):
                    consumer[i].start()
                break
            else:
                break

    def _run_threads(self):
        """run threads.

        helper function when getting images using threading.
        """
        producer = []
        for _ in range(0, self.threads_num):
            p = threading.Thread(target=self._get_img_urls)
            producer.append(p)
        for i in range(0, self.threads_num):
            producer[i].start()
        for i in range(0, self.threads_num):
            producer[i].join()

    def get_imgs_using_threading(self):
        """get imgs using threading."""
        consumer = []
        self._process_tags(total_posts_func=self._run_threads)
        if self.need_save:
            self._process_img_queue(consumer)

    def _check_already_exists(self, name):
        return os.path.isfile(os.path.join(self.save_path, name))

    def _get_img_urls(self):
        """get image urls."""
        # counter for image_limit check
        image_counter = 0
        is_limit_reached = False
        while not self.post_queue.empty():
            limit_start = self.post_queue.get()
            url = '{}{}&num={}&tagged={}'.format(self.base_url, limit_start, self.num, self.tag)
            data = utils.download_page(url, proxies=self.proxies)
            vid_urls = get_video_url(data)

            if data and not is_limit_reached:
                imgs = []
                imgs.extend(self.img_re.findall(data))
                imgs.extend(vid_urls)
                res = self._process_images(
                    images=imgs, image_counter=image_counter, is_limit_reached=is_limit_reached)
                is_limit_reached = res['is_limit_reached']
                image_counter = res['image_counter']

    @staticmethod
    def _check_limit(image_limit, image_counter):
        """check limit.

        Args:
            image_limit (int): Image limit.
            image_counter (int): Image counter.

        Returns:
            bool: Return True if condition is fulfilled and image counter equal or bigger than
            image limit.
        """
        is_limit_reached = False
        # check if limit reached
        if image_limit is not None:
            if image_limit <= image_counter:
                is_limit_reached = True

        return is_limit_reached

    def _process_images_without_save(self, images, image_counter, is_limit_reached):
        """process images without saving them..

        Result is a dict with following keys:
        - is_limit_reached (bool): Return True if limit is reached.
        - image_counter (bool): Image counter for image which put on image queue.

        Args:
            images (list): list of image urls.

        Returns:
            dict: Result of the process
        """
        # compatibility
        imgs = images

        for img in imgs:
            img = img.replace('\\', '')
            self.imglog.info("%s" % img)

            # stop the for-loop if limit reached.
            if is_limit_reached:
                break
        return {
            'is_limit_reached': is_limit_reached,
            'image_counter': image_counter,
        }

    def _process_single_image(self, image, filename, image_counter, is_limit_reached):
        """process single image.

        Args:
            image: Image obj.
            filename: Image filename.
            image_counter (int): Image counter.
            is_limit_reached (bool): State if limit is reached.

        Returns:
            int: Modified image counter.
        """
        # compatibility
        img = image

        # pre process url before put it in queue
        if self._check_already_exists(filename):
            print("Skipping:\t{}".format(filename))
        elif is_limit_reached:
            print("Hit limit, skipping;\t{}".format(filename))
        else:
            print("Queued:\t{}".format(filename))
            self.img_queue.put(img)
            image_counter += 1
        return image_counter

    def _process_images(self, images, image_counter, is_limit_reached):
        """process images.

        Result is a dict with following keys:
        - is_limit_reached (bool): Return True if limit is reached.
        - image_counter (bool): Image counter for image which put on image queue.

        Args:
            images (list): list of image urls.

        Returns:
            dict: Result of the process
        """
        # compatibility
        imgs = images

        if not self.need_save:
            return self._process_images_without_save(images, image_counter, is_limit_reached)

        for img in imgs:
            img = img.replace('\\', '')
            filename = get_filename(img)
            is_limit_reached = self._check_limit(
                image_limit=self.image_limit, image_counter=image_counter)

            image_counter = self._process_single_image(
                image=img, filename=filename, image_counter=image_counter,
                is_limit_reached=is_limit_reached
            )
            # stop the for-loop if limit reached.
            if is_limit_reached:
                break
        return {
            'is_limit_reached': is_limit_reached,
            'image_counter': image_counter,
        }

    def _download_imgs(self):
        if self.need_save:
            while not all((self.img_queue.empty(), self.post_queue.empty())):
                # print self.__str__()
                img_url = self.img_queue.get()
                img_name = get_filename(img_url)
                if not (self.tags and os.path.exists(os.path.join(self.save_path, img_name))):
                    utils.download_imgs(
                        img_url, self.save_path, img_name, self.proxies, stream=self.stream,
                        timeout=self.timeout
                    )

    def _get_total_posts(self):
        """get total posts.

        Returns:
            int: Return total posts.
        """
        url = "{}0&num=1&tagged={}".format(self.base_url, self.tag)
        data = utils.download_page(url)
        if not data:
            return self.total_posts
        self.total_posts = int(self.total_post_re.findall(data)[0])
        if self.max_posts:
            self.total_posts = min(self.total_posts, self.max_posts)
        limit_start = self.limit_start
        while limit_start < self.total_posts:
            self.post_queue.put(limit_start)
            limit_start += self.num
        return self.total_posts

    @staticmethod
    def _create_dir_if_not_exists(path):
        """create dir if not exists"""
        if not os.path.isdir(path):
            os.makedirs(path)

    def _set_default_save_path(self, *args):
        """set default path"""
        path = os.path.join(*args)
        self._create_dir_if_not_exists(path=path)
        self.save_path = path

    def _check_save_path(self):
        """check save path."""
        if not self.save_path or self.save_path is None:
            self._set_default_save_path(os.getcwd(), "imgs/", self.blog)
            return
        if self.save_path.startswith('/'):
            self._create_dir_if_not_exists(self.save_path)
        else:
            self._set_default_save_path(os.getcwd(), "imgs/", self.save_path)

    def __str__(self):
        """str repr."""
        if not self.total_posts:
            self._get_total_posts()
        txt_fmt = "{0} has {1} posts, left {2} json to parse, left {3} imgs to download"
        return txt_fmt.format(
            self.blog, self.total_posts, self.post_queue.qsize(), self.img_queue.qsize()
        )

    __repr__ = __str__


if __name__ == "__main__":  # pragma: no cover
    proxies = {"http": "http://127.0.0.1:13456"}
    dl = Tumblr("er0", need_save=False, proxies=proxies)
    dl.run()
