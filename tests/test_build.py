# coding=utf-8

import unittest
from collections import OrderedDict
from xml.etree import ElementTree
from letterparser import build, parse
from letterparser.generate import output_xml
from letterparser.conf import raw_config, parse_raw_config
from tests import data_path


class TestBuildArticles(unittest.TestCase):

    def setUp(self):
        self.config = parse_raw_config(raw_config('elife'))

    def test_build_articles(self):
        """simple test for coverage of parsing sections"""
        file_name = data_path('sections.docx')
        jats_content = parse.best_jats(file_name, config=self.config)
        articles = build.build_articles(jats_content, config=self.config)
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0].article_type, "decision-letter")
        self.assertEqual(articles[1].article_type, "reply")

    def test_build_articles_no_config(self):
        """simple test for coverage of parsing with no config specified"""
        file_name = data_path('sections.docx')
        jats_content = parse.best_jats(file_name, config=None)
        articles = build.build_articles(jats_content, config=None)
        self.assertEqual(len(articles), 2)

    def test_build_articles_default_preamble(self):
        """build article with a default preamble"""
        jats_content = '<p><bold>Decision letter</bold></p><p>Test</p>'
        articles = build.build_articles(jats_content, config=self.config)
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].article_type, "decision-letter")
        self.assertEqual(articles[0].content_blocks[0].block_type, "boxed-text")
        self.assertEqual(
            articles[0].content_blocks[0].content[0:35],
            "<p>In the interests of transparency")
        self.assertEqual(articles[0].content_blocks[1].block_type, "p")
        self.assertEqual(articles[0].content_blocks[1].content, "Test")

    def test_split_content_sections(self):
        sections = {
            "content": (
                '<p>One<xref xlink:href="" /></p>' +
                '<list><list-item><p>Extra</p></list-item></list><p>Two</p>' +
                '<disp-quote><p>Quotation 1</p><p>Quotation 2</p></disp-quote>')
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
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>Quotation 1</p>')
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>Quotation 2</p>')
            ]),
        ]
        result = build.split_content_sections(sections)
        self.assertEqual(result, expected)

    def test_clean_math_alternatives(self):
        xml_string = (
            '<root xmlns:mml="http://www.w3.org/1998/Math/MathML"><p><disp-formula>' +
            '<alternatives><tex-math><![CDATA[\\beta]]></tex-math><mml:math><mml:mi>β</mml:mi>' +
            '</mml:math></alternatives>' +
            '</disp-formula></p></root>'
        )
        section_xml = ElementTree.fromstring(xml_string)
        expected = (
            b'<?xml version="1.0" encoding="utf-8"?><root xmlns:mml="' +
            b'http://www.w3.org/1998/Math/MathML"><p><disp-formula>' +
            b'<mml:math alttext="\\beta"><mml:mi>\xce\xb2</mml:mi></mml:math>' +
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
        self.assertEqual(result[0].attr, {})
        self.assertEqual(result[0].content, '')

    def test_process_content_sections_disp_quote(self):
        content_sections = [
            OrderedDict([
                ("tag_name", "disp-quote"),
                ("content", '<disp-quote><p>Quotation</p></disp-quote>'),
            ])
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "disp-quote")
        self.assertEqual(result[0].attr, {})
        self.assertEqual(result[0].content, '<p>Quotation</p>')

    def test_process_content_sections_unknown(self):
        content_sections = [
            OrderedDict([
                ("tag_name", None),
                ("content", '<unknown />'),
            ])
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, None)
        self.assertEqual(result[0].attr, {})
        self.assertEqual(result[0].content, '<unknown />')

    def test_process_content_sections_maths(self):
        content_sections = [
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>First Paragraph</p>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p><disp-formula><mml:math alttext="\\beta_{V}"' +
                 ' xmlns:mml="http://www.w3.org/1998/Math/MathML" display="block">' +
                 '<mml:mrow><mml:msub><mml:mi>β</mml:mi><mml:mi>V</mml:mi></mml:msub>' +
                 '</mml:mrow></mml:math></disp-formula></p>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>Second Paragraph</p>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>Third Paragraph</p>'),
            ]),
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "p")
        self.assertEqual(result[0].content, (
            'First Paragraph<disp-formula><mml:math alttext="\\beta_{V}"' +
            ' xmlns:mml="http://www.w3.org/1998/Math/MathML" display="block">' +
            '<mml:mrow><mml:msub><mml:mi>β</mml:mi><mml:mi>V</mml:mi></mml:msub>' +
            '</mml:mrow></mml:math></disp-formula>Second Paragraph'))
        self.assertEqual(result[1].block_type, "p")
        self.assertEqual(result[1].content, (
            'Third Paragraph'))

    def test_process_content_sections_append(self):
        """test case for non-p following a disp-formula p"""
        content_sections = [
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>First Paragraph</p>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p><disp-formula></disp-formula></p>'),
            ]),
            OrderedDict([
                ("tag_name", "list"),
                ("content", '<list list-type="bullet"><list-item></list-item></list>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p><disp-formula></disp-formula></p>'),
            ]),
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "p")
        self.assertEqual(result[0].content, 'First Paragraph<disp-formula></disp-formula>')
        self.assertEqual(result[1].block_type, "list")
        self.assertEqual(result[1].attr, {"list-type": "bullet"})
        self.assertEqual(result[1].content, '<list-item></list-item>')
        self.assertEqual(result[2].block_type, "p")
        self.assertEqual(result[2].content, '<disp-formula></disp-formula>')


class TestDefaultPreamble(unittest.TestCase):

    def test_default_preamble_no_config(self):
        """default preamble if no config specified"""
        self.assertIsNone(build.default_preamble(None))


class TestBuildDoi(unittest.TestCase):

    def setUp(self):
        self.config = parse_raw_config(raw_config('elife'))

    def test_build_doi(self):
        file_name = 'folder/Dutzler 39122 edit.docx'
        id_value = 'sa1'
        expected = '10.7554/eLife.39122.sa1'
        doi = build.build_doi(file_name, id_value, self.config)
        self.assertEqual(doi, expected)

    def test_build_doi_no_file_name(self):
        file_name = None
        id_value = 'sa1'
        doi = build.build_doi(file_name, id_value, self.config)
        self.assertIsNone(doi)

    def test_build_doi_no_config(self):
        file_name = 'folder/Dutzler 39122 edit.docx'
        id_value = 'sa1'
        doi = build.build_doi(file_name, id_value, None)
        self.assertIsNone(doi)
