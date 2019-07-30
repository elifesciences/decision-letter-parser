# coding=utf-8

"utility helper functions"
import sys


def unicode_encode(string):
    "encode to utf8 depending on the python version"
    if sys.version_info[0] < 3:
        string = string.encode('utf8')
    return string
