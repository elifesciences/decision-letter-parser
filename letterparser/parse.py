import re
import pypandoc
from letterparser import utils


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
    return jats_content


def section_type(jats_content, section_map):
    """determine the section type of the jats_content looking at the section_map"""
    content_section_type = None
    for section_type, section_match in list(section_map.items()):
        if jats_content.startswith(section_match):
            content_section_type = section_type
    return content_section_type


def sections(jats_content, root_tag="root"):
    """break the jats_content into sections for sub-article tags"""
    sections = []
    section_map = {
        'decision_letter': '<p><bold>Decision letter</bold></p>',
        'author_response': '<p><bold>Author response</bold></p>'
    }

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
