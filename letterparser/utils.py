# coding=utf-8

"utility helper functions"


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
    "try to decode from utf8"
    try:
        string = string.decode('utf8')
    except (UnicodeEncodeError, AttributeError):
        pass
    return string
