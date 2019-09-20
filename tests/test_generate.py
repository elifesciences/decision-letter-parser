# coding=utf-8

import unittest
from xml.etree.ElementTree import Element
from letterparser import generate
from letterparser.objects import ContentBlock
from tests import data_path, helpers, read_fixture


def simple_decision_letter():
    sub_article = helpers.base_decision_letter()
    preamble_block = ContentBlock("boxed-text")
    preamble_block.content_blocks.append(ContentBlock("p", "Preamble"))
    sub_article.content_blocks.append(preamble_block)
    sub_article.content_blocks.append(ContentBlock("p", (
        "Thank you for submitting your article \"ZZ9 Plural Z α\" to <italic>eLife</italic>.")))
    return sub_article


def simple_author_response():
    sub_article = helpers.base_author_response()
    sub_article.content_blocks.append(ContentBlock("p", "Essential revisions:"))
    disp_quote_block = ContentBlock("disp-quote")
    disp_quote_block.attr["content-type"] = "editor-comment"
    disp_quote_block.content_blocks.append(ContentBlock(
        "p", "1) I am not sure that I understand ...."))
    sub_article.content_blocks.append(disp_quote_block)
    return sub_article


class TestGenerateOutputXML(unittest.TestCase):

    def test_output_xml(self):
        """test non-pretty output of a simple ElementTree object"""
        root = Element("root")
        expected = b'<?xml version="1.0" encoding="utf-8"?><root/>'
        self.assertEqual(generate.output_xml(root), expected)


class TestGenerate(unittest.TestCase):

    def test_generate_simple(self):
        """test generating a simple article"""
        articles = [simple_decision_letter(), simple_author_response()]
        root = generate.generate(articles)
        pretty_xml = generate.output_xml(root, pretty=True, indent="    ")
        expected = read_fixture("generate_simple.xml", mode="rb")
        self.assertEqual(pretty_xml, expected)


class TestGenerateFromDocx(unittest.TestCase):

    def test_generate_xml_from_docx(self):
        """simple test for code coverage"""
        file_name = data_path('Dutzler 39122 edit.docx')
        pretty_xml = generate.generate_xml_from_docx(file_name, pretty=True, indent="    ")
        self.assertIsNotNone(pretty_xml)


class TestGenerateMaxLevel(unittest.TestCase):

    def test_generate_max_level(self):
        """test exceeding the MAX_LEVEL of nested content"""
        max_level_original = generate.MAX_LEVEL
        generate.MAX_LEVEL = 1
        # add two levels of nested content
        article = helpers.base_decision_letter()
        parent_block = ContentBlock("p", "First level paragraph.")
        child_block = ContentBlock("p", "Second level paragraph.")
        parent_block.content_blocks.append(child_block)
        article.content_blocks.append(parent_block)
        articles = [article]
        self.assertRaises(Exception, generate.generate, articles)
        # reset the module MAX_LEVEL value
        generate.MAX_LEVEL = max_level_original
