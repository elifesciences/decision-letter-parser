import re
from collections import OrderedDict
import pypandoc
import requests
from letterparser import docker_lib, utils
from letterparser.conf import raw_config, parse_raw_config


DEFAULT_DOCKER_IMAGE = "pandoc/core:2.7"


SECTION_MAP = {
    "preamble": "<p><bold>Preamble</bold></p>",
    "decision_letter": "<p><bold>Decision letter</bold></p>",
    "author_response": "<p><bold>Author response</bold></p>"
}


def ensure_config(config):
    """populate a default config if it is not specified"""
    if not config:
        config = parse_raw_config(raw_config(None))
    return config


def pandoc_output(file_name):
    try:
        return pypandoc.convert_file(file_name, "jats")
    except OSError:
        # todo!! log exception pandoc is probably not installed locally
        pass


def docker_pandoc_output(file_name, config):
    docker_image = None
    if config:
        docker_image = config.get("docker_image")
    if not docker_image:
        # todo !! log that default docker image was used
        docker_image = DEFAULT_DOCKER_IMAGE
    try:
        return docker_lib.call_pandoc(file_name, docker_image)
    except requests.exceptions.ConnectionError:
        # todo !! log exception - docker may not be running
        pass


def parse_file(file_name, config=None):
    """issue the call to pandoc locally or via docker"""
    output = pandoc_output(file_name)
    if not output:
        output = docker_pandoc_output(file_name, config)
    return output


def raw_jats(file_name, root_tag="root", config=None):
    "convert file content to JATS"
    config = ensure_config(config)
    output = parse_file(file_name, config=config)
    return "<%s>%s</%s>" % (root_tag, output, root_tag)


def clean_jats(file_name, root_tag="root", config=None):
    """cleaner rough JATS output from the raw_jats"""
    config = ensure_config(config)
    jats_content = ""
    raw_jats_content = raw_jats(file_name, root_tag, config=config)
    jats_content = utils.collapse_newlines(raw_jats_content)
    jats_content = utils.remove_non_breaking_space(jats_content)
    return jats_content


def best_jats(file_name, root_tag="root", config=None):
    """from file input, produce the best JATS output possible"""
    config = ensure_config(config)
    clean_jats_content = clean_jats(file_name, root_tag, config=config)
    clean_jats_content = utils.remove_strike(clean_jats_content)
    jats_content = convert_break_tags(clean_jats_content, root_tag)
    # wrap in root_tag
    root_open_tag = "<" + root_tag + ">"
    root_close_tag = "</" + root_tag + ">"
    jats_content = root_open_tag + jats_content + root_close_tag
    return jats_content


def convert_break_tags(jats_content, root_tag="root"):
    """convert break tags to p tags and remove unwanted break tags"""
    converted_jats_content = ""
    # simple fix for italic sandwich
    jats_content = jats_content.replace("<break /><italic><break />", "</p><p><italic>")
    # collapse double break tags into paragraph tags
    break_section_match = "<break /><break />"
    break_section_map = {"": break_section_match}
    break_sections = sections(jats_content, root_tag, break_section_map)
    # hanging tags could possibly be still open across <break /><break /> dividers
    hanging_tags = ["italic", "bold"]
    open_tags = set()
    for i, break_section in enumerate(break_sections):
        content = break_section.get("content")
        content = content.replace(break_section_match, "")
        if i != 0:
            converted_jats_content += "<p>"
            for tag_name in open_tags:
                converted_jats_content += utils.open_tag(tag_name)

        converted_jats_content += content

        if i < len(break_sections)-1:
            # detect and close any open tags
            for tag_name in hanging_tags:
                open_tag_count = content.count(utils.open_tag(tag_name))
                close_tag_count = content.count(utils.close_tag(tag_name))
                first_close_tag_index = content.find(utils.close_tag(tag_name))
                first_open_tag_index = content.find(utils.open_tag(tag_name))
                if open_tag_count > close_tag_count:
                    converted_jats_content += utils.close_tag(tag_name)
                    open_tags.add(tag_name)
                elif (first_close_tag_index and first_open_tag_index and
                      first_close_tag_index < first_open_tag_index):
                    # do the same if tag counts equal but close tag comes before the open tag
                    converted_jats_content += utils.close_tag(tag_name)
                    open_tags.add(tag_name)
                elif tag_name in open_tags:
                    # there are open tags from previous section
                    converted_jats_content += utils.close_tag(tag_name)
                    open_tags.add(tag_name)

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
        section = OrderedDict()
        section["section_type"] = portion_section_type
        section["content"] = portion
        # append it if not empty
        if portion:
            sections.append(section)
        # set for next iteration
        substring_start = string_index

    return sections
