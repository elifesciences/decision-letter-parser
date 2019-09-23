# coding=utf-8

import re
from elifearticle.article import Article
from letterparser import parse
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

        id_value = 'SA%s' % id_count
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
    # first split into paragraphs
    paragraphs = split_paragraphs(section)
    # profile and process into content blocks
    content_blocks = process_paragraphs(paragraphs)
    # add to the article
    article.content_blocks = content_blocks


def split_paragraphs(section):
    """split section content into paragraphs by <p> tags"""
    paragraphs = section.get("content").split("<p>")
    paragraphs = [re.sub('</p>$', '', para) for para in paragraphs if para]
    return paragraphs


def process_paragraphs(paragraphs):
    """profile each paragraph and add as an appropriate content block"""
    content_blocks = []
    for para in paragraphs:
        # todo!!
        content_blocks.append(ContentBlock("p", para))
    return content_blocks
