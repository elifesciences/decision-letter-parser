# coding=utf-8

"utility helper functions"
import os
import sys
import re
from elifetools import xmlio
from elifetools import utils as etoolsutils


# namespaces for when reparsing XML strings
REPARSING_NAMESPACES = (
    'xmlns:ali="http://www.niso.org/schemas/ali/1.0/" ' +
    'xmlns:mml="http://www.w3.org/1998/Math/MathML" ' +
    'xmlns:xlink="http://www.w3.org/1999/xlink"'
)


def remove_non_breaking_space(string):
    """replace non breaking space characters"""
    return string.replace("\xc2\xa0", "").replace("\xa0", "")


def remove_strike(string):
    """replace strike tags and leading and tailing whitespace"""
    if not string:
        return ""
    for match in re.finditer(r'\s*<strike>.*?</strike>\s*', string):
        # replace with blank string unless flanked by spaces replace with a space char
        replace_char = ""
        if match.group(0).startswith(" ") and match.group(0).endswith(" "):
            replace_char = " "
        string = string.replace(match.group(0), replace_char)
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


def allowed_tags():
    """tuple of whitelisted tags"""
    return (
        '<p>', '</p>',
        '<italic>', '</italic>',
        '<bold>', '</bold>',
        '<underline>', '</underline>',
        '<sub>', '</sub>',
        '<sup>', '</sup>',
        '<sc>', '</sc>',
        '<inline-formula>', '</inline-formula>',
        '<disp-formula>', '</disp-formula>',
        '<mml:', '</mml:',
        '<ext-link', '</ext-link>',
        '<list', '</list>',
        '<list-item', '</list-item>',
        '<label>', '</label>',
        '<caption>', '</caption>',
        '<graphic', '</graphic>',
        '<table', '</table>',
        '<thead>', '</thead>',
        '<tbody>', '</tbody>',
        '<tr>', '</tr>',
        '<th>', '</th>',
        '<td', '</td>',
        '<xref', '</xref>'
    )


def append_to_parent_tag(parent, tag_name, original_string,
                         namespaces=REPARSING_NAMESPACES, attributes=None, attributes_text=''):
    """escape and reparse the string then add it to the parent tag"""
    tag_converted_string = etoolsutils.escape_ampersand(original_string)
    tag_converted_string = etoolsutils.escape_unmatched_angle_brackets(
        tag_converted_string, allowed_tags())
    minidom_tag = xmlio.reparsed_tag(
        tag_name, tag_converted_string, namespaces, attributes_text)
    xmlio.append_minidom_xml_to_elementtree_xml(
        parent, minidom_tag, attributes=attributes, child_attributes=True)


def get_file_name_path(file_name):
    """return the folder path to a file excluding the file name itself"""
    return os.sep.join(file_name.split(os.sep)[0:-1])


def get_file_name_file(file_name):
    """return the file name only removing the folder path preceeding it"""
    return file_name.split(os.sep)[-1]
