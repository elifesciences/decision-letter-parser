# coding=utf-8

"utility helper functions"
import os
import re
from elifetools import xmlio
from elifetools import utils as etoolsutils


# namespaces for when reparsing XML strings
XML_NAMESPACE_MAP = {
    "ali": "http://www.niso.org/schemas/ali/1.0/",
    "mml": "http://www.w3.org/1998/Math/MathML",
    "xlink": "http://www.w3.org/1999/xlink",
}


def reparsing_namespaces(namespace_map):
    """compile a string representation of the namespaces"""
    namespace_string = ""
    for prefix, uri in namespace_map.items():
        namespace_string += 'xmlns:%s="%s" ' % (prefix, uri)
    return namespace_string.rstrip()


def remove_non_breaking_space(string):
    """replace non breaking space characters"""
    return string.replace("\xc2\xa0", "").replace("\xa0", "") if string else ""


def remove_strike(string):
    """replace strike tags and leading and tailing whitespace"""
    if not string:
        return ""
    for match in re.finditer(r"\s*<strike>.*?</strike>\s*", string):
        # replace with blank string unless flanked by spaces replace with a space char
        replace_char = ""
        if match.group(0).startswith(" ") and match.group(0).endswith(" "):
            replace_char = " "
        string = string.replace(match.group(0), replace_char)
    return string


def remove_empty_p_tags(string):
    """remove paragraphs which only contain whitespace"""
    if not string:
        return ""
    empty_p_tag_match_pattern = re.compile(r"<p[^>]*?>\s+?</p>")
    return re.sub(empty_p_tag_match_pattern, "", string)


def new_line_replace_with(line_one, line_two):
    """determine the whitespace to use when concatenating two lines together"""
    if line_one is None:
        return ""

    # strip spaces before comparisons
    line_one = line_one.lstrip().rstrip()
    line_two = line_two.lstrip().rstrip()

    if line_one.endswith(">") and line_two.startswith("<"):
        if (
            line_one.startswith("<p><italic>")
            and not line_one.endswith("</italic></p>")
            and line_two.startswith("</italic>")
        ):
            return "</italic><break /><break /><italic>"
        # default return blank string
        return ""

    if not line_one.startswith("<p>"):
        if line_two == "<italic>":
            return "<break /><break />"
        if line_one.endswith("</italic>"):
            return "<break /><break />"
        if line_one.startswith("</italic>") and line_two.startswith("<italic>"):
            return "<break /><break />"
        if (
            not line_one.startswith("<")
            and line_two.startswith("</italic>")
            and line_two != "</italic></p>"
        ):
            return "<break /><break />"
        if line_two.startswith("<bold>") and line_two.endswith("</bold></p>"):
            return "<break /><break />"
        if not line_two.startswith("<") and line_two.endswith("</p>"):
            return "<break /><break />"
        if not line_two.endswith("</p>") and not line_one.startswith("<"):
            return "<break /><break />"
    elif line_two == "<italic>":
        return "<break /><break />"
    elif not line_one.endswith(">") and line_two.startswith("<italic>"):
        return "<break /><break />"
    elif (
        line_one != "<p><italic>"
        and line_one.endswith("<italic>")
        and not line_two.startswith("<")
    ):
        return "</italic><break /><break /><italic>"
    elif (
        line_one.startswith("<p><italic>")
        and not line_one.endswith("</italic></p>")
        and line_two.startswith("</italic>")
        and line_two != "</italic></p>"
    ):
        return "</italic><break /><break /><italic>"
    elif not line_one.endswith(">") and not line_two.startswith("<"):
        return "<break /><break />"
    elif (
        not line_one.endswith(">")
        and line_two.startswith("<bold>")
        and line_two.endswith("</p>")
    ):
        return "<break /><break />"
    return ""


def collapse_newlines(string):
    if not string:
        return None
    new_string = ""
    prev_line = None
    for line in string.split("\n"):
        replace_with = new_line_replace_with(prev_line, line.lstrip())
        new_string += replace_with + line.lstrip()
        prev_line = line
    # remove meaningless break and italic tags due to and edge case fix
    new_string = new_string.replace(
        "<break /><break /></italic><break /><break />", "</italic><break /><break />"
    )
    new_string = new_string.replace(
        "<break /><break /></italic>", "</italic><break /><break />"
    )
    new_string = new_string.replace(
        "<break /><break /><italic><break /><break />", "<break /><break /><italic>"
    )
    new_string = new_string.replace("<italic></italic>", "")
    return new_string


def clean_portion(string, root_tag="root"):
    if not string:
        return ""
    string = re.sub(r"^<" + root_tag + ".*?>", "", string)
    string = re.sub(r"</" + root_tag + ">$", "", string)
    return string.lstrip().rstrip()


def allowed_tags():
    """tuple of whitelisted tags"""
    return (
        "<p>",
        "<p ",
        "</p>",
        "<disp-quote",
        "</disp-quote>",
        "<italic>",
        "</italic>",
        "<bold>",
        "</bold>",
        "<underline>",
        "</underline>",
        "<sub>",
        "</sub>",
        "<sup>",
        "</sup>",
        "<sc>",
        "</sc>",
        "<inline-formula>",
        "</inline-formula>",
        "<disp-formula>",
        "</disp-formula>",
        "<mml:",
        "</mml:",
        "<ext-link",
        "</ext-link>",
        "<list>",
        "<list ",
        "</list>",
        "<list-item",
        "</list-item>",
        "<label>",
        "</label>",
        "<title>",
        "</title>",
        "<caption>",
        "</caption>",
        "<graphic ",
        "</graphic>",
        "<table",
        "<table ",
        "</table>",
        "<thead>",
        "</thead>",
        "<tbody>",
        "</tbody>",
        "<tr>",
        "</tr>",
        "<th>",
        "<th",
        "</th>",
        "<td>",
        "<td ",
        "</td>",
        "<xref ",
        "</xref>",
    )


def append_to_parent_tag(
    parent,
    tag_name,
    original_string,
    namespace_map,
    attributes=None,
    attributes_text="",
):
    """escape and reparse the string then add it to the parent tag"""
    tag_converted_string = etoolsutils.escape_ampersand(original_string)
    tag_converted_string = etoolsutils.escape_unmatched_angle_brackets(
        tag_converted_string, allowed_tags()
    )
    namespaces_string = reparsing_namespaces(namespace_map)
    minidom_tag = xmlio.reparsed_tag(
        tag_name, tag_converted_string, namespaces_string, attributes_text
    )
    xmlio.append_minidom_xml_to_elementtree_xml(
        parent, minidom_tag, attributes=attributes, child_attributes=True
    )


def xml_string_fix_namespaces(xml_string, root_tag):
    """due to some bug with ElementTree.tostring, remove duplicate namespace attributes"""
    # remove duplicate namespaces from root tag e.g. xmlns:mml="http://www.w3.org/1998/Math/MathML
    root_tag_bytes = bytes(root_tag, "utf8")
    match_string = rb"^(<%s.*?>).*" % root_tag_bytes
    root_tag_match = re.match(match_string, xml_string)
    if not root_tag_match:
        return xml_string
    root_tag_string = root_tag_match.group(1)  # original root tag string
    # extract all tag attributes separated by a space
    attributes = root_tag_string.rstrip(b">").split(b" ")[1:]
    # de-dupe the attributes using set comprehension
    unique_attributes = {attr for attr in attributes if attr}
    # join the unique attributes alphabetically
    attributes_string = b" ".join(sorted(unique_attributes))
    # assemble the string to replace the original root tag string
    new_root_tag_string = b"<%s %s>" % (root_tag_bytes, attributes_string)
    # now can replace the string
    return xml_string.replace(root_tag_string, new_root_tag_string)


def replace_character_entities(xml_string):
    """replace standard XML character entities with hexadecimal replacements"""
    char_map = {
        b"&amp;": b"&#x0026;",
        b"&gt;": b"&#x003E;",
        b"&lt;": b"&#x003C;",
        b"&quot;": b"&#x0022;",
    }
    for from_char, to_char in char_map.items():
        try:
            xml_string = xml_string.replace(from_char, to_char)
        except TypeError:
            # convert string to bytes if required
            xml_string = xml_string.encode("utf8").replace(from_char, to_char)
    return xml_string


def get_file_name_path(file_name):
    """return the folder path to a file excluding the file name itself"""
    return os.sep.join(file_name.split(os.sep)[0:-1])


def get_file_name_file(file_name):
    """return the file name only removing the folder path preceeding it"""
    return file_name.split(os.sep)[-1]


def open_tag(tag_name, attr=None):
    if not attr:
        return "<%s>" % tag_name
    attr_values = []
    for name, value in sorted(attr.items()):
        attr_values.append('%s="%s"' % (name, value))
    return "<%s %s>" % (tag_name, " ".join(attr_values))


def close_tag(tag_name):
    return "</%s>" % tag_name


def manuscript_from_file_name(file_name):
    # todo!!!
    # may requiring changing when final file name format is decided
    # based on file name e.g. Dutzler 39122 edit.docx
    if file_name:
        first_file_name_part = get_file_name_file(file_name).split(".")[0]
        spaced_parts = first_file_name_part.split(" ")
        hyphenated_parts = first_file_name_part.split("-")
        if len(spaced_parts) > 1:
            manuscript_string = spaced_parts[1]
        else:
            manuscript_string = hyphenated_parts[1]
        try:
            return str(int(manuscript_string))
        except ValueError:
            return None
    return None


def remove_complex_scripts_styles(document_xml):
    """given docx document.xml contents remove complex scripts style tags"""

    # pattern for matching run tags w:r
    run_tag_match_pattern = re.compile(rb"(<w:r\s+.*?>.*?</w:r>)")
    # pattern for matching complex styles bold formatting tags
    complex_bold_match_pattern = re.compile(rb"<w:bCs.*?/>")
    # pattern for matching complex styles italic formatting tags
    complex_italic_match_pattern = re.compile(rb"<w:iCs.*?/>")

    new_document_xml = b""
    for xml_part in re.split(run_tag_match_pattern, document_xml):
        # if the w:rFonts tag contains a specific attribute, then do not remove the complex styles
        if not (b"<w:rFonts" in xml_part and b"w:cstheme" in xml_part) or (
            b"<w:rFonts" in xml_part and b"w:ascii" in xml_part
        ):
            xml_part = re.sub(complex_bold_match_pattern, b"", xml_part)
            xml_part = re.sub(complex_italic_match_pattern, b"", xml_part)
        new_document_xml += xml_part

    return new_document_xml
