import re
import pypandoc
from letterparser import utils


SECTION_MAP = {
    "decision_letter": "<p><bold>Decision letter</bold></p>",
    "author_response": "<p><bold>Author response</bold></p>"
}


def raw_jats(file_name, root_tag="root"):
    "convert file content to JATS"
    jats_content = ""
    output = pypandoc.convert_file(file_name, "jats")
    jats_content = "<%s>%s</%s>" % (root_tag, utils.unicode_encode(output), root_tag)
    return jats_content


def clean_jats(file_name, root_tag="root"):
    """cleaner rough JATS output from the raw_jats"""
    jats_content = ""
    raw_jats_content = raw_jats(file_name, root_tag)
    jats_content = utils.collapse_newlines(raw_jats_content)
    jats_content = utils.remove_non_breaking_space(jats_content)
    return jats_content


def best_jats(file_name, root_tag="root"):
    """from file input, produce the best JATS output possible"""
    clean_jats_content = clean_jats(file_name, root_tag)
    jats_content = convert_break_tags(clean_jats_content, root_tag)
    # wrap in root_tag
    root_open_tag = "<" + root_tag + ">"
    root_close_tag = "</" + root_tag + ">"
    jats_content = root_open_tag + jats_content + root_close_tag
    return jats_content


def convert_break_tags(jats_content, root_tag="root"):
    """convert break tags to p tags and remove unwanted break tags"""
    converted_jats_content = ""
    # collapse double break tags into paragraph tags
    break_section_match = "<break /><break />"
    break_section_map = {"": break_section_match}
    break_sections = sections(jats_content, root_tag, break_section_map)
    for i, break_section in enumerate(break_sections):
        content = list(break_section.values())[0]
        content = content.replace(break_section_match, "")
        if i != 0:
            converted_jats_content += "<p>"
        converted_jats_content += content
        if i < len(break_sections)-1:
            converted_jats_content += "</p>"
    # remove other break tags
    return converted_jats_content.replace("<break />", "")


def section_type(jats_content, section_map):
    """determine the section type of the jats_content looking at the section_map"""
    content_section_type = None
    for section_type, section_match in list(section_map.items()):
        if jats_content.startswith(section_match):
            content_section_type = section_type
    return content_section_type


def sections(jats_content, root_tag="root", section_map=None):
    """break the jats_content into sections for sub-article tags"""
    sections = []
    if not section_map:
        section_map = SECTION_MAP
    # find the string indicies for the section markers
    string_indexes = [0]
    for section_marker in list(section_map.values()):
        string_indexes += [match.start() for match in re.finditer(section_marker, jats_content)]
    string_indexes.append(len(jats_content))
    # add sections
    for i, string_index in enumerate(sorted(string_indexes)):
        if i == 0:
            # set the substring_start from the first 0 index
            substring_start = string_index
            continue
        portion = utils.clean_portion(jats_content[substring_start:string_index], root_tag)
        # set the section type based on the match string
        portion_section_type = section_type(portion, section_map)
        # populate the section
        section = {portion_section_type: portion}
        # append it
        sections.append(section)
        # set for next interation
        substring_start = string_index

    return sections
