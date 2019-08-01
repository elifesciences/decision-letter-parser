# coding=utf-8

"utility helper functions"
import sys
import re


def unicode_encode(string):
    "encode to utf8 depending on the python version"
    if sys.version_info[0] < 3:
        string = string.encode('utf8')
    return string


def new_line_replace_with(line_one, line_two):
    """determine the whitespace to use when concatenating two lines together"""
    if line_one is None or (line_one.endswith('>') and line_two.startswith('<')):
        return ""
    return " "


def collapse_newlines(string):
    if not string:
        return None
    new_string = ""
    prev_line = None
    for line in string.split("\n"):
        replace_with = new_line_replace_with(prev_line, line)
        new_string += replace_with + line
        prev_line = line
    return new_string


def clean_portion(string, root_tag="root"):
    if not string:
        return ""
    string = re.sub(r'^<' + root_tag + '>', '', string)
    string = re.sub(r'</' + root_tag + '>$', '', string)
    return string.lstrip().rstrip()
