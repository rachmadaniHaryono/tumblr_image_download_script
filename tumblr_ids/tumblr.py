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
#-*-coding:utf-8-*-
try:
    from queue import Queue  # py3
except ImportError:
    from Queue import Queue  # py2
import os
import re
import sys
import threading
import utils


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
        self.total_post_re = total_post_re if total_post_re else re.compile(r'"posts-total":"*(\d+)"*,')
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
        else:
            from mylogger import get_logger
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

    def get_imgs(self):
        """get img."""
        for tag in self.tags:
            self.tag = tag
            print("Tag: " + self.tag)
            if not self.total_posts:
                self._get_total_posts()
            if self.total_posts:
                self._get_img_urls()
            self.total_posts = 0
        if self.need_save:
            if not self.img_queue.empty():
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

    def get_imgs_using_threading(self):
        """get imgs using threading."""
        consumer = []
        for tag in self.tags:
            self.tag = tag
            print("Tag: " + self.tag)
            if not self.total_posts:
                self._get_total_posts()
            if self.total_posts:
                producer = []
                for i in range(0, self.threads_num):
                    p = threading.Thread(target=self._get_img_urls)
                    producer.append(p)
                for i in range(0, self.threads_num):
                    producer[i].start()
                for i in range(0, self.threads_num):
                    producer[i].join()
            self.total_posts = 0

        if self.need_save:
            self._process_img_queue(consumer)

    def _check_already_exists(self, name):
        if os.path.isfile(os.path.join(self.save_path, name)):
            return True
        else:
            return False

    def _get_img_urls(self):
        """get image urls."""
        # counter for image_limit check
        image_counter = 0
        is_limit_reached = False
        while not self.post_queue.empty():
            limit_start = self.post_queue.get()
            url = self.base_url + str(limit_start) + "&num=" + str(self.num) + "&tagged=" + self.tag
            data = utils.download_page(url, proxies=self.proxies)
            vid_urls = get_video_url(data)

            if data and not is_limit_reached:
                imgs = []
                imgs.extend(self.img_re.findall(data))
                imgs.extend(vid_urls)
                for img in imgs:
                    img = img.replace('\\', '')
                    filename = get_filename(img)
                    if not self.need_save:
                        self.imglog.info("%s" % img)
                    else:
                        # check if limit reached
                        if self.image_limit is not None and self.image_limit <= image_counter:
                            is_limit_reached = True
                        else:
                            is_limit_reached = False

                        # pre process url before put it in queue
                        if self._check_already_exists(filename):
                            print("Skipping:\t" + filename)
                        elif is_limit_reached:
                            print("Hit limit, skipping;\t" + filename)
                        else:
                            print("Queued:\t" + filename)
                            self.img_queue.put(img)
                            image_counter += 1

                    # stop the loop if limit reached.
                    if is_limit_reached:
                        break

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
        url = self.base_url + "0&num=1&tagged=" + self.tag
        data = utils.download_page(url)
        if data:
            self.total_posts = int(self.total_post_re.findall(data)[0])
            if self.max_posts:
                self.total_posts = min(self.total_posts, self.max_posts)
            limit_start = self.limit_start
            while limit_start < self.total_posts:
                self.post_queue.put(limit_start)
                limit_start += self.num

    def _check_save_path(self):
        if not self.save_path:
            path = os.path.join(os.getcwd(), "imgs/", self.blog)
            if not os.path.isdir(path):
                os.makedirs(path)
            self.save_path = path
        else:
            if self.save_path.startswith('/'):
                if not os.path.isdir(self.save_path):
                    try:
                        os.makedirs(self.save_path)
                    except Exception as e:
                        print(e)
                        sys.exit(1)
                else:
                    """ 检测有无读写权限 """
                    if not os.access(self.save_path, os.R_OK | os.W_OK):
                        print("invalid save_path {0}".format(self.save_path))
                        sys.exit(1)
            else:
                path = os.path.join(os.getcwd(), "imgs/", self.save_path)
                if not os.path.isdir(path):
                    os.makedirs(path)
                self.save_path = path

    def __str__(self):
        """str repr."""
        if not self.total_posts:
            self._get_total_posts()
        txt_fmt = "{0} has {1} posts, left {2} json to parse, left {3} imgs to download"
        return txt_fmt.format(
            self.blog, self.total_posts, self.post_queue.qsize(), self.img_queue.qsize()
        )

    __repr__ = __str__


def test():
    """test func."""
    proxies = {"http": "http://127.0.0.1:13456"}
    dl = Tumblr("er0", need_save=False, proxies=proxies)
    dl.run()

if __name__ == "__main__":
    test()
