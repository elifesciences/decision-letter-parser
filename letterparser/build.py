# coding=utf-8

import re
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from collections import OrderedDict
import elifearticle.utils as eautils
from elifearticle.article import Article
from letterparser import parse, utils
from letterparser.objects import ContentBlock
from letterparser.conf import raw_config, parse_raw_config


def default_preamble(config):
    if config and config.get("preamble"):
        return OrderedDict([
            ("section_type", "preamble"),
            ("content", config.get("preamble")),
        ])
    return None


def build_articles(jats_content, file_name=None, config=None):
    sections = parse.sections(jats_content)

    if not config:
        config = parse_raw_config(raw_config(None))

    articles = []
    preamble_section = None
    id_count = 1
    for section in sections:
        # detect the preamble sections
        if section.get("section_type") == "preamble":
            preamble_section = section
            continue

        # set the default preamble
        if not preamble_section:
            preamble_section = default_preamble(config)

        id_value = 'sa%s' % id_count

        # set the DOI, if possible
        doi = build_doi(file_name, id_value, config)

        if section.get("section_type") == "decision_letter":
            article = build_decision_letter(section, preamble_section, id_value)
        else:
            article = build_sub_article(section, "reply", id_value, doi)
        articles.append(article)
        # reset the counter
        id_count += 1
        # reset the preamble section
        preamble_section = None

    return articles


def build_doi(file_name, id_value, config):
    if file_name and config and config.get("doi_pattern"):
        return config.get("doi_pattern").format(
            manuscript=utils.manuscript_from_file_name(file_name),
            id=id_value)
    return None


def build_decision_letter(section, preamble_section=None, id_value=None, doi=None):
    article = build_sub_article(section, "decision-letter", id_value, doi)
    # process the preabmle section
    if preamble_section:
        preamble_section = trim_section_heading(preamble_section)
        preamble_block = ContentBlock("boxed-text", preamble_section.get("content"))
        article.content_blocks = [preamble_block] + article.content_blocks
    return article


def build_sub_article(section, article_type=None, id_value=None, doi=None):
    article = Article(doi)
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
        if block_tag.tag in ["list", "p", "table", "disp-quote"]:
            # add p tags from disp-quote blocks
            if block_tag.tag == "disp-quote":
                for p_tag in block_tag.findall("./p"):
                    append_tag_to_sections(content_sections, p_tag)
            else:
                append_tag_to_sections(content_sections, block_tag)
    return content_sections


def append_tag_to_sections(sections, tag):
    content_section = OrderedDict()
    rough_string = element_to_string(tag)
    content_section["tag_name"] = tag.tag
    content_section["content"] = rough_string
    sections.append(content_section)


def element_to_string(tag):
    rough_string = ElementTree.tostring(tag, 'utf8').decode('utf8')
    rough_string = rough_string.replace("<?xml version='1.0' encoding='utf8'?>", "")
    rough_string = rough_string.lstrip("\n")
    return rough_string


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


def build_fig(content):
    # todo!!! convert content into individual elements
    fig_content = OrderedDict()
    fig_content['label'] = 'Author response image 1.'
    fig_content['title'] = 'Author response image 1.'
    fig_content['content'] = 'Caption <sup>2+</sup> calculated using<disp-formula><mml:math alttext="\\alpha"><mml:mi>α</mml:mi></mml:math></disp-formula><disp-formula><mml:math alttext="\\beta"><mml:mi>β</mml:mi></mml:math></disp-formula>and those on the right panels using<disp-formula><mml:math alttext="\\gamma"><mml:mi>γ</mml:mi></mml:math></disp-formula>under symmetrical ionic conditions. The number of barriers <inline-formula><mml:math alttext="n" display="inline"><mml:mi>n</mml:mi></mml:math></inline-formula> have their usual meanings.'
    return fig_content


def fig_element(label, title, content):
    """populate an XML Element for a fig"""
    fig_tag = Element('fig')
    label_tag = SubElement(fig_tag, 'label')
    label_tag.text = label

    caption_tag = SubElement(fig_tag, 'caption')
    title_tag = SubElement(caption_tag, 'title')
    title_tag.text = title

    # append content as a p tag in the caption
    utils.append_to_parent_tag(caption_tag, 'p', content, utils.XML_NAMESPACE_MAP)

    graphic_tag = SubElement(fig_tag, 'graphic')
    graphic_tag.set('mimetype', 'image')
    graphic_tag.set('xlink:href', 'todo')
    return fig_tag


def fig_element_to_string(tag):
    rough_string = element_to_string(tag)
    return utils.clean_portion(rough_string, "fig")


def process_content_sections(content_sections):
    """profile each paragraph and add as an appropriate content block"""
    content_blocks = []
    appended_content = ''
    prev_content = None
    prev_action = None
    prev_tag_name = None
    prev_attr = None
    prev_fig = None
    # add a blank section for the final loop
    content_sections.append(OrderedDict())
    for section in content_sections:
        tag_name = section.get("tag_name")
        content, tag_name, attr, action, fig = process_content(
            tag_name, section.get("content"), prev_content, prev_fig)
        if prev_fig and not fig:
            # finish the fig tag content
            appended_content = appended_content + content
            # todo!!! format the content into the figure content block
            fig_content = build_fig(appended_content)
            fig_tag = fig_element(
                fig_content.get('label'),
                fig_content.get('title'),
                fig_content.get('content'))
            content_block_content = fig_element_to_string(fig_tag)
            content_blocks.append(ContentBlock("fig", content_block_content, prev_attr))
            prev_content = None
            appended_content = ''
        elif action == "add":
            if prev_action == "append":
                content_blocks.append(ContentBlock(prev_tag_name, appended_content, prev_attr))
            content_blocks.append(ContentBlock(tag_name, content, attr))
            prev_content = None
            appended_content = ''
        elif action == "append":
            appended_content = appended_content + content
            prev_content = content
        prev_action = action
        prev_tag_name = tag_name
        prev_attr = attr
        prev_fig = fig

    return content_blocks


def process_content(tag_name, content, prev_content, fig=None):
    if tag_name == "list":
        return process_list_content(content, fig)
    elif tag_name == "table":
        return process_table_content(content), "table", None, "add", fig
    elif tag_name == "p":
        return process_p_content(content, prev_content, fig)
    elif tag_name == "disp-quote":
        return process_disp_quote_content(content, fig)
    # default
    return content, None, None, "add", fig


def process_table_content(content):
    return content


def process_list_content(content, fig=None):
    # simple replacement of list-type="order" with list-type="number"
    content = content.replace('<list list-type="order">', '<list list-type="number">')
    content = eautils.remove_tag("disp-quote", content)
    content_xml = ElementTree.fromstring(content)
    return utils.clean_portion(content, "list"), "list", content_xml.attrib, "add", fig


def process_p_content(content, prev_content, fig=None):
    """set paragraph content and decide to append or add to previous paragraph content"""
    action = "append"
    tag_name = "p"
    if not fig:
        fig = False
    content = utils.clean_portion(content, "p")
    # author response image parsing
    # todo!!! better string matching including non-one number in the string
    if content == '&lt;Author response image 1&gt;':
        fig = True
        content = ''

    if content.endswith('&lt;/Author response image 1 title/legend&gt;'):
        action = "add"
        fig = False
    elif (not fig and prev_content and not prev_content.startswith('<disp-formula') and
          not content.startswith('<disp-formula')):
        action = "add"

    return content, tag_name, None, action, fig


def process_disp_quote_content(content, fig=None):
    return utils.clean_portion(content, "disp-quote"), "disp-quote", None, "add", fig
