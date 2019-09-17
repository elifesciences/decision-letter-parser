# coding=utf-8

from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from letterparser import build, parse, utils


# max level of recursion adding content blocks supported
MAX_LEVEL = 5


def set_if_value(element, name, value):
    """set Element attribute if the value is not empty"""
    if value:
        element.set(name, value)


def generate_xml_from_docx(file_name, root_tag="root", pretty=False, indent=""):
    """generate JATS output from docx file_name"""
    articles = docx_to_articles(file_name, root_tag)
    jats_xml = generate(articles)
    return output_xml(jats_xml, pretty, indent)


def docx_to_articles(file_name, root_tag="root"):
    """convert the docx file to Article objects"""
    jats_content = parse.best_jats(file_name, root_tag)
    return build.build_articles(jats_content)


def generate(articles, root_tag="root"):
    """from jats_content generate final JATS output"""
    # Create the root XML node
    root = Element(root_tag)
    # set namespaces
    root.set('xmlns:mml', 'http://www.w3.org/1998/Math/MathML')
    root.set('xmlns:xlink', 'http://www.w3.org/1999/xlink')
    for article in articles:
        sub_article_tag = SubElement(root, "sub-article")
        set_if_value(sub_article_tag, "article-type", article.article_type)
        set_if_value(sub_article_tag, "id", article.id)
        set_front_stub(sub_article_tag, article)
        set_body(sub_article_tag, article)
    # todo!!!! - set mml:math tag id attributes
    return root


def set_front_stub(parent, article):
    front_stub_tag = SubElement(parent, "front-stub")
    if article.title:
        title_group_tag = SubElement(front_stub_tag, "title-group")
        article_title_tag = SubElement(title_group_tag, "article-title")
        article_title_tag.text = article.title
    # todo!!! continue to fill in the front-stub tag


def set_body(parent, article):
    body_tag = SubElement(parent, "body")
    set_content_blocks(body_tag, article.content_blocks)
    return body_tag


def set_content_blocks(parent, content_blocks, level=1):
    if level > MAX_LEVEL:
        raise Exception('Maximum level of nested content blocks reached')
    for block in content_blocks:
        block_tag = None
        if block.block_type in ["boxed-text", "disp-formula", "disp-quote", "list", "p"]:
            # retain standard tag attributes as well as any specific ones from the block object
            if block.content:
                utils.append_to_parent_tag(
                    parent, block.block_type, block.content, attributes=block.attr_names(),
                    attributes_text=block.attr_string())
                block_tag = parent[-1]
            else:
                # add empty tags too
                block_tag = SubElement(parent, block.block_type)
                block_tag.text = block.content
                for key, value in block.attr.items():
                    block_tag.set(key, value)
        if block_tag is not None and block.content_blocks:
            # recursion
            set_content_blocks(block_tag, block.content_blocks, level+1)


def output_xml(root, pretty=False, indent=""):
    """output root XML Element to a string"""
    encoding = 'utf-8'
    rough_string = ElementTree.tostring(root, encoding)
    reparsed = minidom.parseString(rough_string)

    if pretty is True:
        return reparsed.toprettyxml(indent, encoding=encoding)
    return reparsed.toxml(encoding=encoding)
