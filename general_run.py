#!/usr/bin/env python
# -*-coding:utf-8-*-
from tumblr import Tumblr
import re


def readblogs(filename):
    f = open(filename, 'r')
    blogs = []
    count = 0
    print("Reading blogs.txt...")
    for user in f:
        if not user[0] == '#':
            # remove txt formatting junk
            user = user.strip()
            # remove url junk
            user = re.sub(r"\.tumblr\.com/?.+", "", user)
            user = re.sub(r"http://", "", user)
            blogs.append(Tumblr(user))
        else:
            count += 1
    if count > 0:
        print("Skipped " + str(count) + " lines/users in blogs.txt\n")
    return blogs


def run():
    blogs = readblogs('blogs.txt')
    print("Download/Update for the following Tumblr blogs? \n███ BLOGS ███")
    for user in blogs:
        print(user.blog)
    print("█████████████")
    if input("\nEnter \"y\" to proceed\n") == 'y':
        print("Running..\n")
        for blog in blogs:
            blog.run()
    else:
        print("\nQuitting - No files will be downloaded")


if __name__ == "__main__":
    run()

