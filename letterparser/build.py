# coding=utf-8

import re
from xml.etree import ElementTree
from collections import OrderedDict
from elifearticle.article import Article
from letterparser import parse, utils
from letterparser.objects import ContentBlock


def build_articles(jats_content):
    sections = parse.sections(jats_content)

    articles = []
    preamble_section = None
    id_count = 1
    for section in sections:
        # detect the preamble sections
        if section.get("section_type") == "preamble":
            preamble_section = section
            continue

        id_value = 'sa%s' % id_count
        if section.get("section_type") == "decision_letter":
            article = build_decision_letter(section, preamble_section, id_value)
        else:
            article = build_sub_article(section, "reply", id_value)
        articles.append(article)
        # reset the counter
        id_count += 1
        # reset the preamble section
        preamble_section = None

    return articles


def build_decision_letter(section, preamble_section=None, id_value=None):
    article = build_sub_article(section, "decision-letter", id_value)
    # todo !!!  process the preabmle section

    return article


def build_sub_article(section, article_type=None, id_value=None):
    article = Article()
    article.id = id_value
    if article_type:
        article.article_type = article_type
    # add the content
    article.content_blocks = []
    set_title(article)
    set_content_blocks(article, section)

    return article


def set_title(article):
    """set the article title"""
    # for now use boilerplate values based on the article_type
    title_map = {
        "decision-letter": "Decision letter",
        "reply": "Author response"
    }
    article.title = title_map.get(article.article_type)


def trim_section_heading(section):
    for fragment in parse.SECTION_MAP.values():
        match = r'^' + fragment
        section["content"] = re.sub(match, '', section.get("content"))
    return section


def set_content_blocks(article, section):
    """set the body content blocks"""
    # trim away the section heading
    section = trim_section_heading(section)
    # split into content sections
    content_sections = split_content_sections(section)
    # profile and process into content blocks
    content_blocks = process_content_sections(content_sections)
    # add to the article
    article.content_blocks = content_blocks


def split_content_sections(section):
    """split first child level tags into content parts"""
    content_sections = []
    # register namespaces
    for prefix, uri in utils.XML_NAMESPACE_MAP.items():
        ElementTree.register_namespace(prefix, uri)
    # parse content
    xml_string = '<root %s>%s</root>' % (
        utils.reparsing_namespaces(utils.XML_NAMESPACE_MAP),
        section.get("content"))
    section_xml = ElementTree.fromstring(xml_string)

    # clean the math alternatives here
    section_xml = clean_math_alternatives(section_xml)

    for block_tag in section_xml.findall("./*"):
        content_section = OrderedDict()
        if block_tag.tag in ["list", "p", "table"]:
            rough_string = ElementTree.tostring(block_tag, 'utf8').decode('utf8')
            rough_string = rough_string.replace("<?xml version='1.0' encoding='utf8'?>", "")
            rough_string = rough_string.lstrip("\n")
            content_section["tag_name"] = block_tag.tag
            content_section["content"] = rough_string
        content_sections.append(content_section)
    return content_sections


def clean_math_alternatives(section_xml):
    """use mml:math from the <alternatives> tag"""
    for formula_tag in (section_xml.findall(".//disp-formula") +
                        section_xml.findall(".//inline-formula")):
        mml_tag = formula_tag.find(
            './/{http://www.w3.org/1998/Math/MathML}math', utils.XML_NAMESPACE_MAP)
        tex_math_tag = formula_tag.find('.//tex-math')
        mml_tag.set("alttext", tex_math_tag.text)
        alt_tag = formula_tag.find('./alternatives')
        formula_tag.remove(alt_tag)
        formula_tag.append(mml_tag)
    return section_xml


def process_content_sections(content_sections):
    """profile each paragraph and add as an appropriate content block"""
    content_blocks = []
    prev_section = None
    for section in content_sections:
        # todo!! format the content
        content = process_content(section.get("tag_name"), section.get("content"))
        content_blocks.append(ContentBlock(section.get("tag_name"), content))
        prev_section = section
    return content_blocks


def process_content(tag_name, content):
    if tag_name == "list":
        return process_list_content(content)
    elif tag_name == "table":
        return process_table_content(content)
    elif tag_name == "p":
        return process_p_content(content)
    return content


def process_table_content(content):
    return content


def process_list_content(content):
    return content


def process_p_content(content):
    # todo !!
    content = utils.clean_portion(content, "p")
    return content
    # if content.startswith('<disp-formula'):
    #    pass
