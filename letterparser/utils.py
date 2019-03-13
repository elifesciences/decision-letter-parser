# coding=utf-8
import os


def get_file_name_path(file_name):
    """return the folder path to a file excluding the file name itself"""
    return os.sep.join(file_name.split(os.sep)[0:-1])


def get_file_name_file(file_name):
    """return the file name only removing the folder path preceeding it"""
    return file_name.split(os.sep)[-1]


def unicode_encode(string):
    """safely encode string as utf8 by catching exceptions"""
    if string is None or isinstance(string, str):
        return string
    try:
        string = string.encode('utf8')
    except (UnicodeDecodeError, TypeError, AttributeError):
        string = unicode_decode(string)
    return string


def unicode_decode(string):
    """try to decode from utf8"""
    try:
        string = string.decode('utf8')
    except (UnicodeEncodeError, AttributeError):
        pass
    return string
