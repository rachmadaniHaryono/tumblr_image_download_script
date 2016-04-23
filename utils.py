# !/usr/bin/env python
# -*-coding:utf-8-*-

"""
    通用程序
"""
import sys
import os
import requests

from mylogger import get_logger
dllog = get_logger("app")

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except NameError:
    # The only supported default encodings in Python are:

    #  Python 2.x: ASCII
    #  Python 3.x: UTF-8
    # So no need to sys.setdefaultencoding('utf-8')
    pass # py3


# 执行 requests 的数据下载
def download_page(url, ret_json=False, proxies=None):
    if not url:
        dllog.info("url should not be None")
        return ''

    try:
        dllog.info("当前下载的 url: %s " % url)
        r = requests.get(url, proxies=proxies, timeout=10)
        if r.status_code == 200:
            if ret_json:
                return r.json()
            # r.text is decoded string
            # r.content is binary response content(bytes)
            # see http://docs.python-requests.org/en/latest/user/quickstart/#binary-response-content
            return r.text
        else:
            dllog.info("下载失败，status_code: %s" % r.status_code)
            return ''

    except Exception as e:
        dllog.info("下载失败, %s %s" % (url, e))
        return ''


def download_imgs(url, path, name, proxies=None):
    try:
        dllog.info("当前下载的 url: %s " % url)
        r = requests.get(url, stream=True, proxies=proxies, timeout=10)
        file = os.path.join(path, name)
        if os.path.isfile(file):
            print("Skipping - File already exists:" + name)
            return
        with open(file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)
        print("Downloading: " + name)
    except Exception as e:
        dllog.info("下载失败, %s %s" % (url, e))


def test():
    pass

if __name__ == "__main__":
    test()
