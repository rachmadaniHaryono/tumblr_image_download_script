#!/usr/bin/env python
# -*-coding:utf-8-*-
"""
mylogger.py.

#=============================================================================
# FileName:     mylogger.py
# Desc:         python logger support zip log file
# Author:       leyle
# Email:        leyle@leyle.com
# HomePage:     http://www.leyle.com/
# Git_page:     https://github.com/leyle
# Version:      0.1.2
# LastChange:   2015-03-10 11:09:59
#=============================================================================
"""
import logging
import logging.handlers
import sys
import os

LOGGING_MSG_FORMAT = "%(name)s %(levelname)s %(asctime)s: %(message)s"
LOGGING_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_BYTE = 1024 * 1024 * 50


def create_new_logfile_path(path):
    """ create new log file path, pwd+path.

    Args:
        path: New path.

    Returns:
        Modified path.
    """
    path = os.path.join(sys.path[0], path)
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def process_path_as_folder(path):
    """process path as folder.

    Args:
        path: Path
    """
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except OSError as e:
            print(e)
            sys.exit(1)
    elif not os.access(path, os.R_OK | os.W_OK):
        print(path, "without read/write permission")
        sys.exit(1)


def get_logger(logfile, path="logs/", level=logging.DEBUG, max_byte=MAX_BYTE, backup_count=10):
    """get logger."""
    root_logger = logging.getLogger(logfile)
    if len(root_logger.handlers) != 0:
        return root_logger
    if path.startswith('/'):
        # assuming path is folder
        process_path_as_folder(path)
    else:
        path = create_new_logfile_path(path=path)
    if not path.endswith('/'):
        path = '{}/'.format(path)

    handler = logging.handlers.RotatingFileHandler(
        '{}{}.log'.format(path, logfile),
        mode="a",
        maxBytes=max_byte,
        backupCount=backup_count,
        encoding="utf-8"
    )

    fmter = logging.Formatter(LOGGING_MSG_FORMAT, LOGGING_DATE_FORMAT)
    handler.setFormatter(fmter)
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    return logging.getLogger(logfile)


if __name__ == "__main__":
    # get_logger(
    # logfile, path="logs/", level=logging.DEBUG, max_byte=1024*1024*50, backup_count=10):
    mylog = get_logger("log_name", "abc/def", max_byte=100)
    for i in range(0, 10000):
        mylog.info("%d" % i)
