# coding=utf-8

from elifearticle.article import Article
from letterparser import parse


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
    # todo !!!  add the content
    article.content_blocks = []

    return article
