# coding=utf-8

"utility helper functions"
import os
import sys
import re
from elifetools import xmlio
from elifetools import utils as etoolsutils


# namespaces for when reparsing XML strings
XML_NAMESPACE_MAP = {
    'ali': 'http://www.niso.org/schemas/ali/1.0/',
    'mml': 'http://www.w3.org/1998/Math/MathML',
    'xlink': 'http://www.w3.org/1999/xlink'
}


def reparsing_namespaces(namespace_map):
    """compile a string representation of the namespaces"""
    namespace_string = ''
    for prefix, uri in namespace_map.items():
        namespace_string += 'xmlns:%s="%s" ' % (prefix, uri)
    return namespace_string.rstrip()


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
        replace_with = new_line_replace_with(prev_line, line.lstrip())
        new_string += replace_with + line.lstrip()
        prev_line = line
    return new_string


def clean_portion(string, root_tag="root"):
    if not string:
        return ""
    string = re.sub(r'^<' + root_tag + '.*?>', '', string)
    string = re.sub(r'</' + root_tag + '>$', '', string)
    return string.lstrip().rstrip()


def allowed_tags():
    """tuple of whitelisted tags"""
    return (
        '<p>', '<p ', '</p>',
        '<disp-quote', '</disp-quote>',
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
        '<list>', '<list ', '</list>',
        '<list-item', '</list-item>',
        '<label>', '</label>',
        '<title>', '</title>',
        '<caption>', '</caption>',
        '<graphic ', '</graphic>',
        '<table', '<table ', '</table>',
        '<thead>', '</thead>',
        '<tbody>', '</tbody>',
        '<tr>', '</tr>',
        '<th>', '</th>',
        '<td>', '<td ', '</td>',
        '<xref ', '</xref>'
    )


def append_to_parent_tag(parent, tag_name, original_string,
                         namespace_map, attributes=None, attributes_text=''):
    """escape and reparse the string then add it to the parent tag"""
    tag_converted_string = etoolsutils.escape_ampersand(original_string)
    tag_converted_string = etoolsutils.escape_unmatched_angle_brackets(
        tag_converted_string, allowed_tags())
    namespaces_string = reparsing_namespaces(namespace_map)
    minidom_tag = xmlio.reparsed_tag(
        tag_name, tag_converted_string, namespaces_string, attributes_text)
    xmlio.append_minidom_xml_to_elementtree_xml(
        parent, minidom_tag, attributes=attributes, child_attributes=True)


def get_file_name_path(file_name):
    """return the folder path to a file excluding the file name itself"""
    return os.sep.join(file_name.split(os.sep)[0:-1])


def get_file_name_file(file_name):
    """return the file name only removing the folder path preceeding it"""
    return file_name.split(os.sep)[-1]


def open_tag(tag_name):
    return "<%s>" % tag_name


def close_tag(tag_name):
    return "</%s>" % tag_name


def manuscript_from_file_name(file_name):
    # todo!!!
    # may requiring changing when final file name format is decided
    # based on file name e.g. Dutzler 39122 edit.docx
    if file_name:
        first_file_name_part = get_file_name_file(file_name).split('.')[0]
        spaced_parts = first_file_name_part.split(' ')
        hyphenated_parts = first_file_name_part.split('-')
        if len(spaced_parts) > 1:
            manuscript_string = spaced_parts[1]
        else:
            manuscript_string = hyphenated_parts[1]
        try:
            return str(int(manuscript_string))
        except ValueError:
            return None
    return None
