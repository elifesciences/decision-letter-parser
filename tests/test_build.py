# coding=utf-8

import unittest
from collections import OrderedDict
from xml.etree import ElementTree
from letterparser import build, parse
from letterparser.generate import output_xml
from tests import data_path


class TestBuildArticles(unittest.TestCase):

    def test_build_articles(self):
        """simple test for coverage of parsing sections"""
        file_name = data_path('sections.docx')
        jats_content = parse.best_jats(file_name)
        articles = build.build_articles(jats_content)
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0].article_type, "decision-letter")
        self.assertEqual(articles[1].article_type, "reply")

    def test_split_content_sections(self):
        sections = {
            "content": (
                '<p>One<xref xlink:href="" /></p>' +
                '<list><list-item><p>Extra</p></list-item></list><p>Two</p>')
            }
        expected = [
            OrderedDict([
                ("tag_name", "p"),
                ("content", (
                    '<p xmlns:xlink="http://www.w3.org/1999/xlink">' +
                    'One<xref xlink:href="" /></p>')
                )
            ]),
            OrderedDict([
                ("tag_name", "list"),
                ("content", '<list><list-item><p>Extra</p></list-item></list>')
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>Two</p>')
            ]),
        ]
        result = build.split_content_sections(sections)
        self.assertEqual(result, expected)

    def test_clean_math_alternatives(self):
        xml_string = (
            '<root xmlns:mml="http://www.w3.org/1998/Math/MathML"><p><disp-formula>' +
            '<alternatives><tex-math></tex-math><mml:math></mml:math></alternatives>' +
            '</disp-formula></p></root>'
        )
        section_xml = ElementTree.fromstring(xml_string)
        expected = (
            b'<?xml version="1.0" encoding="utf-8"?><root xmlns:mml="' +
            b'http://www.w3.org/1998/Math/MathML"><p><disp-formula><mml:math/>' +
            b'</disp-formula></p></root>'
        )
        clean_element = build.clean_math_alternatives(section_xml)
        xml_string = output_xml(clean_element)
        self.assertEqual(xml_string, expected)

    def test_process_content_sections(self):
        content_sections = [
            OrderedDict([
                ("tag_name", "p"),
                ("content", 'Hello!'),
            ])
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "p")
        self.assertEqual(result[0].content, "Hello!")

    def test_process_content_sections_namespace(self):
        content_sections = [
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p xmlns:xlink="http://www.w3.org/1999/xlink">Hello!</p>'),
            ])
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "p")
        self.assertEqual(result[0].content, "Hello!")

    def test_process_content_sections_table(self):
        content_sections = [
            OrderedDict([
                ("tag_name", "table"),
                ("content", '<table></table>'),
            ])
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "table")
        self.assertEqual(result[0].content, '<table></table>')

    def test_process_content_sections_list(self):
        content_sections = [
            OrderedDict([
                ("tag_name", "list"),
                ("content", '<list></list>'),
            ])
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "list")
        self.assertEqual(result[0].content, '<list></list>')
