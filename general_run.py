#!/usr/bin/env python
# -*-coding:utf-8-*-
from tumblr import Tumblr
import re
import time


def readblogs(filename):
    f = open(filename, 'r')
    blogs = []
    count = 0
    print("Reading blogs.txt...")
    for user in f:
        if not len(user) < 2:
            if user[0] == '#':
                pass
            elif (user[0]+user[1]) == "--":
                count += 1
            else:
                # remove txt formatting junk
                user = user.strip()
                # remove url junk
                user = re.sub(r"\.tumblr\.com/?.+", "", user)
                user = re.sub(r"http://", "", user)
                user = re.sub(r"www\.", "", user)
                blogs.append(Tumblr(user))
    if count > 0:
        print("Skipped " + str(count) + " lines/users in blogs.txt\n")
    return blogs


def run():
    blogs = readblogs('blogs.txt')
    if len(blogs) == 0:
        print("No blogs found in blogs.txt")
    else:
        print("Download/Update for the following Tumblr blogs? \n███ BLOGS ███")
        for user in blogs:
            print(user.blog)
        print("█████████████")
        if input("Proceed? (y/n)\n") == 'y':
            if input("Use safe mode (slower, recommended) (y/n)") == 'y':
                start = time.time()
                for blog in blogs:
                    blog.run(use_threading=False, stream=False, timeout=None)
                end = time.time()
                print("\n--Downloading Finished--\nTime Elapsed: " + str(round((end - start))) + "s")
            else:
                print("Running..")
                for blog in blogs:
                print("\n--Downloading started--\n")
        else:
            print("\nQuitting - No files will be downloaded")


if __name__ == "__main__":
    run()

