#!/usr/bin/env python
# -*-coding:utf-8-*-
from tumblr import Tumblr
import re
import time
import argparse
import sys


def readblogs(filename):
    blogs = []
    count = 0
    try:
        f = open(filename, 'r')
    except FileNotFoundError:
        return blogs
    print("Reading " + filename + "...")
    for user in f:
        if not len(user) < 2:
            if user[0] == '#':
                pass
            elif (user[0]+user[1]) == "--":
                count += 1
            else:
                # remove txt formatting junk
                user = user.strip()
                # get tags
                tags = user.split(';;')
                if len(tags) > 1:
                    tags = tags[1]
                    tags = tags.split(',')
                else:
                    tags = ['']
                #print(tags)
                # remove url junk
                user = re.sub(r"\.tumblr\.com/?.+", "", user)
                user = re.sub(r"https?://", "", user)
                user = re.sub(r"www\.", "", user)
                user = re.sub(r";;.+", "", user)
                blogs.append(Tumblr(user, tags=tags))
    if count > 0:
        print("Skipped " + str(count) + " lines/users in " + filename + "\n")
    return blogs


def run(noinfo, stream, threading, timeout, filename, proxy, image_limit=None):
    """run the program.

    :param image_limit: limit the downloaded image."""
    # print("\ninfo: " + str(info))
    # print("\nstream: " + str(stream))
    # print("\nthreading: " + str(threading))
    # print("\ntimeout: " + str(timeout))
    # print("\nfilename: " + str(filename))
    blogs = readblogs(filename)
    if len(blogs) == 0:
        print("No blogs found in " + filename + ".\n")
        if noinfo:
            sys.exit(0)
        if input("Would you like to generate an example file called example.txt? (y/n)\n") == 'y':
            example = open('example.txt', 'w')
            example.write("#This line is a comment")
            example.write("\n#Use -- to skip blogs:")
            example.write("\n--http://inactive-artist.tumblr.com/")
            example.write("\n\n#Blogs can be listed in Username format or URL format")
            example.write("\n\n#Username Format")
            example.write("\nlazy-artist")
            example.write("\n\n#URL Format")
            example.write("\nhttp://cool-artist.tumblr.com/")
            example.write("\n#TAG Format")
            example.write("http://reblogging-artist.tumblr.com/;;original-post,cute")
            example.write("\n\n#If used, this file will try to download from "
                          "\"cool-artist\", \"lazy-artist\" and \"reblogging-artist\" but not \"inactive-artist\"")
            example.write("#From \"reblogging-artist\", it will only download posts tagged \"original-post\" "
                          "or \"cute\" (Helpful for filtering out blogs that reblog a lot "
                          "but have a tag for their original content")
    else:
        if not noinfo:
            print("Download/Update for the following Tumblr blogs? \n███ BLOGS ███")
            for user in blogs:
                print(user.blog)
            print("█████████████")
            print("With the following settings:")
            print("stream: " + str(stream))
            print("threading: " + str(threading))
            print("timeout: " + str(timeout))
            print("█████████████")
            if input("Proceed? (y/n)\n") != 'y':
                print("Quitting - No files will be downloaded")
                sys.exit(0)
        print("Running...\n")
        start = time.time()
        for blog in blogs:
            blog.run(use_threading=threading, stream=stream, timeout=timeout, proxies=proxy,
                     image_limit=image_limit)
        if not threading:
            end = time.time()
            print("\n--Downloading Finished--\nTime Elapsed: " + str(round((end - start))) + "s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Downloads all images from blogs specified in blogs.txt. "
                                                 "Blogs can be formatted as a username: \"username\" "
                                                 "or in URL form: \"http://username.tumblr.com/*\". "
                                                 "Blogs may be skipped by starting the line with --. "
                                                 "Lines starting with # are comments.")
    parser.add_argument('-i', '--noinfo', action='store_true', help="Doesn't show blog list or ask for confirmation")
    parser.add_argument('-s', '--stream', action='store_true', help="Files downloaded are streamed")
    parser.add_argument('-t', '--threading', action='store_true', help="Download using threading")
    parser.add_argument('-n', '--timeout', help="Specify download timeout in seconds (Default is none)")
    parser.add_argument('-f', '--filename', default="blogs.txt", help="Specify alternate filename for blogs.txt")
    parser.add_argument('-p', '--proxy', default=None, help="Specify proxy in the form \'protocol://host:port\'")
    parser.add_argument('-l', '--limit', default=None, help="Limit the download image.")
    args = parser.parse_args()
    if args.proxy is not None:
        proxies = {args.proxy.split(':')[0]: args.proxy}
    else:
        proxies = None

    # clean args.limit input
    if args.limit:
        args.limit = int(args.limit)
        # set to 0 if actual value is less than 0
        args.limit = 0 if args.limit < 0 else args.limit

    print(str(proxies))
    run(args.noinfo, args.stream, args.threading, args.timeout, args.filename, proxies,
        image_limit=args.limit)
    sys.exit(0)
