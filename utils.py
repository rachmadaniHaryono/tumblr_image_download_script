#!/usr/bin/env python
#-*-coding:utf-8-*-

"""
    通用程序
"""
import sys
import os
import requests

from mylogger import get_logger
dllog = get_logger("app")

reload(sys)
sys.setdefaultencoding('utf-8')

# 执行 requests 的数据下载
def download_page(url, ret_json=False):
    if not url:
        dllog.info("url 不合法: %s" % url)
        return ''

    try:
        dllog.info("当前下载的 url: %s " % url)
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            if ret_json:
                return r.json()
            return r.content
        else:
            dllog.info("下载失败，status_code: %s" % r.status_code)
            return ''

    except Exception as e:
        dllog.info("下载失败, %s %s" % (url, e))
        return ''

def download_imgs(url, path, name):
    try:
        dllog.info("当前下载的 url: %s " % url)
        r = requests.get(url, stream=True, timeout=10)
        file = os.path.join(path, name)
        with open(file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)
    except Exception as e:
        dllog.info("下载失败, %s %s" % (url, e))

def test():
    pass

if __name__ == "__main__":
    test()
