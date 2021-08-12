import re
from collections import OrderedDict
import pypandoc
import requests
from letterparser import docker_lib, utils, zip_lib
from letterparser.conf import raw_config, parse_raw_config


DEFAULT_DOCKER_IMAGE = "pandoc/core:2.9.1.1"


SECTION_MAP = {
    "editors_evaluation": "<p><bold>Editors evaluation</bold></p>",
    "preamble": "<p><bold>Preamble</bold></p>",
    "decision_letter": "<p><bold>Decision letter</bold></p>",
    "author_response": "<p><bold>Author response</bold></p>",
}


def ensure_config(config):
    """populate a default config if it is not specified"""
    if not config:
        config = parse_raw_config(raw_config(None))
    return config


def pandoc_output(file_name):
    try:
        return pypandoc.convert_file(file_name, to="jats", extra_args=["--wrap=none"])
    except OSError:
        # todo!! log exception pandoc is probably not installed locally
        pass
    return None


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
    return None


def parse_file(file_name, config=None, temp_dir="tmp"):
    """issue the call to pandoc locally or via docker"""
    # make a copy of the file and fix complex scripts styles inside the docx
    new_file_name = zip_lib.fix_complex_scripts_styles(file_name, temp_dir)
    output = pandoc_output(new_file_name)
    if not output:
        output = docker_pandoc_output(new_file_name, config)
    return output


def raw_jats(file_name, root_tag="root", config=None, temp_dir="tmp"):
    "convert file content to JATS"
    config = ensure_config(config)
    output = parse_file(file_name, config=config, temp_dir=temp_dir)
    return "<%s>%s</%s>" % (root_tag, output, root_tag)


def clean_jats(file_name, root_tag="root", config=None, temp_dir="tmp"):
    """cleaner rough JATS output from the raw_jats"""
    config = ensure_config(config)
    jats_content = ""
    raw_jats_content = raw_jats(file_name, root_tag, config=config, temp_dir=temp_dir)
    jats_content = utils.collapse_newlines(raw_jats_content)
    return jats_content


def best_jats(file_name, root_tag="root", config=None, temp_dir="tmp"):
    """from file input, produce the best JATS output possible"""
    config = ensure_config(config)
    clean_jats_content = clean_jats(
        file_name, root_tag, config=config, temp_dir=temp_dir
    )
    clean_jats_content = utils.remove_strike(clean_jats_content)
    # remove empty paragraphs
    jats_content = utils.remove_empty_p_tags(clean_jats_content)
    # convert sec tags
    jats_content = convert_sec_tags(jats_content)
    # convert break tags
    jats_content = convert_break_tags(jats_content, root_tag)
    # wrap in root_tag
    root_open_tag = "<" + root_tag + ">"
    root_close_tag = "</" + root_tag + ">"
    jats_content = root_open_tag + jats_content + root_close_tag
    return jats_content


def convert_sec_tags(jats_content):
    """remove sec tags and convert title to p tag"""
    match_string = r"(<sec.*?>.*</sec>)"
    sec_tag_match = re.finditer(match_string, jats_content)
    for match_group in sec_tag_match:
        original_string = match_group.group(1)  # original string
        # replace first title tag with p tag
        new_string = re.sub(r"<sec.*?><title.*?>", "<p>", original_string)
        new_string = re.sub(r"<sec.*?><title.*?>", "<p>", original_string)
        new_string = re.sub(r"</title>", "</p>", new_string)
        # remove sec close tag
        new_string = re.sub(r"</sec>", "", new_string)
        # replace in original string
        jats_content = jats_content.replace(original_string, new_string)
    return jats_content


def convert_break_tags(jats_content, root_tag="root"):
    """convert break tags to p tags and remove unwanted break tags"""
    converted_jats_content = ""
    # simple fix for italic sandwich
    jats_content = jats_content.replace("<break /><italic><break />", "</p><p><italic>")

    # replace break tags in tables first
    jats_content = re.sub(
        r"<td(.*?)<break /><break />(.*?)</td>", r"<td\1<break />\2</td>", jats_content
    )
    jats_content = re.sub(
        r"<th(.*?)<break /><break />(.*?)</th>", r"<th\1<break />\2</th>", jats_content
    )

    # collapse double break tags into paragraph tags
    break_section_match = "<break /><break />"
    break_section_map = {"": break_section_match}
    break_sections = sections(jats_content, root_tag, break_section_map)
    # add blank content to the end for last iteration
    break_sections.append({"content": ""})
    # hanging tags could possibly be still open across <break /><break /> dividers
    hanging_tags = ["italic", "bold"]
    open_tags = set()
    for i, break_section in enumerate(break_sections):
        content = break_section.get("content")

        content = content.replace(break_section_match, "")

        if 0 < i < len(break_sections) - 1:
            for tag_name in open_tags:
                content = utils.open_tag(tag_name) + content
            if not content.startswith("<p>"):
                content = "<p>" + content

        if i < len(break_sections) - 1:
            # detect and close any open tags
            for tag_name in hanging_tags:
                open_tag_count = content.count(utils.open_tag(tag_name))
                close_tag_count = content.count(utils.close_tag(tag_name))
                first_close_tag_index = content.find(utils.close_tag(tag_name))
                first_open_tag_index = content.find(utils.open_tag(tag_name))
                if open_tag_count == close_tag_count and tag_name in open_tags:
                    open_tags.remove(tag_name)

                if open_tag_count > close_tag_count and tag_name not in open_tags:
                    content += utils.close_tag(tag_name)
                    open_tags.add(tag_name)
                elif (
                    first_close_tag_index
                    and first_open_tag_index
                    and first_close_tag_index < first_open_tag_index
                ):
                    # do the same if tag counts equal but close tag comes before the open tag
                    content += utils.close_tag(tag_name)
                    open_tags.add(tag_name)
                elif tag_name in open_tags:
                    # there are open tags from previous section
                    content += utils.close_tag(tag_name)
                    open_tags.add(tag_name)

            if (
                not content.endswith("</p>")
                and not content.endswith("</table>")
                and not content.endswith("</disp-quote>")
                and not content.endswith("</list>")
            ):
                content += "</p>"

        converted_jats_content += content

    # remove other break tags
    return converted_jats_content


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
        string_indexes += [
            match.start() for match in re.finditer(section_marker, jats_content)
        ]
    string_indexes.append(len(jats_content))
    # add sections
    for i, string_index in enumerate(sorted(string_indexes)):
        if i == 0:
            # set the substring_start from the first 0 index
            substring_start = string_index
            continue
        portion = utils.clean_portion(
            jats_content[substring_start:string_index], root_tag
        )
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
