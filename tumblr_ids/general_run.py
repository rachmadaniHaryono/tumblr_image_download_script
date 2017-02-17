#!/usr/bin/env python
# -*-coding:utf-8-*-
"""main module."""
import argparse
import pprint
import re
import sys
import time

from .tumblr import Tumblr


def format_tumblr_input(user):
    """format tumblr input.

    return (formatted_user, and tags).
    """
    # remove txt formatting junk
    user = user.strip()
    # get tags
    tags = user.split(';;')
    if len(tags) > 1:
        tags = tags[1]
        tags = tags.split(',')
    else:
        tags = ['']
    # print(tags)
    # remove url junk
    user = re.sub(r"\.tumblr\.com/?.+", "", user)
    user = re.sub(r"https?://", "", user)
    user = re.sub(r"www\.", "", user)
    user = re.sub(r";;.+", "", user)
    return user, tags


def process_file(file_obj):
    """process file.

    key for return vars:
    - blogs: Formatted blog.
    - count: Skipped line/user.

    Args:
        file_obj: File object to be processed.

    Returns:
        dict: Processing result.
    """
    # compatibility
    f = file_obj

    blogs = []
    count = 0
    for user in f:
        if not len(user) < 2:
            if user[0] == '#':
                pass
            elif (user[0] + user[1]) == "--":
                count += 1
            else:
                user, tags = format_tumblr_input(user)
                blogs.append(Tumblr(user, tags=tags))
    return {
        'blogs': blogs,
        'count': count
    }


def readblogs(filename):
    """read blog from filename."""
    blogs = []
    count = 0
    try:
        f = open(filename, 'r')
    except OSError:  # alternative to FileNotFoundError
        return blogs
    print("Reading " + filename + "...")

    res = process_file(file_obj=f)
    blogs = res['blogs']
    count = res['count']

    if count > 0:
        print("Skipped " + str(count) + " lines/users in " + filename + "\n")
    return blogs


def get_readable_time(seconds):
    """convert second into readable time."""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)

    result = '{}h'.format(h) if h > 0 else ''
    result += '{}m'.format(m) if m > 0 else ''
    result += '{}s'.format(s) if s > 0 else ''
    return result


def write_example():
    """write example."""
    if input("Would you like to generate an example file called example.txt? (y/n)\n") == 'y':
        example = open('example.txt', 'w')
        example.write("""#This line is a comment
#Use -- to skip blogs:
--http://inactive-artist.tumblr.com/

#Blogs can be listed in Username format or URL format

#Username Format
lazy-artist

#URL Format
http://cool-artist.tumblr.com/

#TAG Format
http://reblogging-artist.tumblr.com/;;original-post,cute

#If used, this file will try to download
#from "cool-artist", "lazy-artist" and "reblogging-artist", but not "inactive-artist"
#From "reblogging-artist",
#it will only download posts tagged "original-post" or "cute"
#(Helpful for filtering out blogs that reblog a lot
#but have a tag for their original content)
""")


def print_info(blogs, stream, threading, timeout):
    """print info.

    Args:
        blogs (list): Tumblr blogs.
        stream (bool): True to make the download to be streamed.
        threading (bool): True to make download using threading.
        timeout (int): Download timeout in seconds (Default is none)
    """
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


def print_elapsed_time(start_time):
    """print elapsed time.

    Args:
        start_time (int): Start time.
    """
    # compatibility
    start = start_time

    end = time.time()
    elapsed_time = get_readable_time(round((end - start)))
    txt_fmt = "\n--Downloading Finished--\nTime Elapsed: {}"
    print(txt_fmt.format(elapsed_time))


def run(noinfo, stream, threading, timeout, filename, proxy, image_limit=None, tumblr_input=None):
    """run the program.

    Args:
        noinfo (bool): True if to not show blog list or ask for confirmation.
        stream (bool): True to make the download to be streamed.
        threading (bool): True to make download using threading.
        timeout (int): Download timeout in seconds (Default is none)
        filename : Filename for blogs.txt
        proxy (str): Proxy to download.
        image_limit (int): Limit the downloaded image.
        tumblr_input (str): Additional tumblr input from user.
    """
    # print("\ninfo: " + str(info))
    # print("\nstream: " + str(stream))
    # print("\nthreading: " + str(threading))
    # print("\ntimeout: " + str(timeout))
    # print("\nfilename: " + str(filename))

    # read from text file.
    blogs = readblogs(filename)

    # append additional tumblr input if exist.
    if tumblr_input is not None:
        user, tags = format_tumblr_input(tumblr_input)
        blogs.append(Tumblr(user, tags=tags))

    # check if no tumble input given or existed.
    if len(blogs) == 0:
        print("No blogs found in " + filename + ".\n")
        if noinfo:
            sys.exit(0)
        write_example()
        return

    # process input
    if not noinfo:
        print_info()
    print("Running...\n")
    start = time.time()
    list(map(
        lambda x:
        x.run(
            use_threading=threading, stream=stream, timeout=timeout, proxies=proxy,
            image_limit=image_limit
        ),
        blogs
    ))
    if not threading:
        print_elapsed_time(start_time=start)


def check_positive(value):
    """check if value is positive.

    taken and modified from http://stackoverflow.com/a/14117511

    Args:
        value: Value

    Return:
        int: Integer from value.
    """
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def check_proxy(value):
    """check if given proxy valid and process it.

    modified from check_positive func.

    Args:
        value: Value

    Return:
        dict: Formatted proxy.
    """
    if value is not None:
        proxies = {value.split(':')[0]: value}
    else:
        proxies = None
    print('Proxy: {}'.format(pprint.pformat(proxies)))
    return proxies


def get_args(argv):
    """get parsed arguments.

    Args:
        argv (list): List of arguments.

    Returns
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(description=(
        "Downloads all images from blogs specified in blogs.txt. "
        "Blogs can be formatted as a username: \"username\" "
        "or in URL form: \"http://username.tumblr.com/*\". "
        "Blogs may be skipped by starting the line with --. "
        "Lines starting with # are comments.")
    )
    parser.add_argument(
        '-i', '--noinfo', action='store_true',
        help="Doesn't show blog list or ask for confirmation"
    )
    parser.add_argument(
        '-s', '--stream', action='store_true', help="Files downloaded are streamed"
    )
    parser.add_argument(
        '-t', '--threading', action='store_true', help="Download using threading"
    )
    parser.add_argument(
        '-n', '--timeout', help="Specify download timeout in seconds (Default is none)"
    )
    parser.add_argument(
        '-f', '--filename', default="blogs.txt", help="Specify alternate filename for blogs.txt"
    )
    parser.add_argument(
        '-p', '--proxy', default=None, help="Specify proxy in the form \'protocol://host:port\'",
        type=check_proxy
    )
    parser.add_argument(
        '--tumblr-input', metavar='TUMBLR', default=None, help="Tumblr user input."
    )
    parser.add_argument(
        '-l', '--limit', default=None, help="Limit the download image.", type=check_positive
    )
    args = parser.parse_args(argv)
    return args


def main(argv):
    """main function."""
    args = get_args(argv)

    run(
        args.noinfo, args.stream, args.threading, args.timeout, args.filename, args.proxies,
        image_limit=args.limit, tumblr_input=args.tumblr_input
    )


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
