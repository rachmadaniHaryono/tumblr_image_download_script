# !/usr/bin/env python
# -*-coding:utf-8-*-

u"""通用程序 (gt: General Procedure.)."""
import sys
import os
import requests
import time

from mylogger import get_logger
dllog = get_logger(time.strftime("%d-%m-%Y+%H-%M-%S"))

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except NameError:
    # The only supported default encodings in Python are:

    #  Python 2.x: ASCII
    #  Python 3.x: UTF-8
    # So no need to sys.setdefaultencoding('utf-8')
    pass  # py3


# 执行 requests 的数据下载
def download_page(url, ret_json=False, proxies=None):
    """download  page."""
    if not url:
        dllog.info("url should not be None")
        return ''

    try:
        dllog.info("当前下载的(Current Download) url: %s " % url)
        r = requests.get(url, proxies=proxies, timeout=10)
        if r.status_code == 200:
            if ret_json:
                return r.json()
            # r.text is decoded string
            # r.content is binary response content(bytes)
            # see http://docs.python-requests.org/en/latest/user/quickstart/#binary-response-content
            return r.text
        else:
            dllog.info("下载失败(Download Failed)，status_code: %s" % r.status_code)
            return ''
    except Exception as e:
        dllog.info("下载失败 Download Failed), %s %s" % (url, e))
        return ''


def download_imgs(url, path, name, proxies=None, stream=True, timeout=10):
    """download imgs."""
    try:
        dllog.info("当前下载的(Current Download) url: %s " % url)
        r = requests.get(url, stream=stream, proxies=proxies, timeout=timeout)
        file = os.path.join(path, name)
        print("Downloading:\t" + name)
        with open(file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)
    except Exception as e:
        dllog.info("下载失败(Download Failed), %s %s" % (url, e))


def test():
    """test func."""
    pass

if __name__ == "__main__":
    test()
