# coding=utf-8

import unittest
from collections import OrderedDict
from xml.etree import ElementTree
from elifearticle.article import Article, ContentBlock
from letterparser import build, parse
from letterparser.generate import output_xml
from letterparser.conf import raw_config, parse_raw_config
from tests import data_path, read_fixture


class TestBuildArticles(unittest.TestCase):

    def setUp(self):
        self.config = parse_raw_config(raw_config('elife'))
        # prefs for author_response sections
        self.prefs = OrderedDict()
        self.prefs['italic_to_disp_quote'] = True

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

    def test_build_articles_disp_quote_italic(self):
        """buggy situation where two italic tags are in a disp-quote content p"""
        jats_content = (
            '<p><bold>Author response</bold></p><p><italic>A series of important changes is'
            ' requested before the manuscript could be</italic> <italic>considered for'
            ' publication in eLife.</italic></p><p><italic>1) The authors need to do'
            ' .....</italic></p>')
        articles = build.build_articles(jats_content, config=self.config)
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].article_type, "reply")
        self.assertEqual(articles[0].content_blocks[0].block_type, "disp-quote")
        self.assertEqual(
            articles[0].content_blocks[0].content[0:52],
            "<p>A series of important changes is requested before")

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

    def test_split_content_sections_author_response_image(self):
        """parse author response image snippet of content JATS into sections"""
        section = OrderedDict([
            ('section_type', 'author_response'),
            ('content', read_fixture('author_response_image_1.txt'))
        ])
        expected = read_fixture('author_response_image_1_sections.py')
        sections = build.split_content_sections(section)
        self.assertEqual(sections, expected)

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

    def test_process_content_sections_table_with_caption(self):
        content_sections = [
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<italic>Italic paragraph.</italic>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<italic>Previous paragraph.</italic>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<bold>Author response Table 1.</bold>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", (
                    '&lt;Author response table 1 title/legend&gt;Author response table'
                    '&lt;/Author response table 1 title/legend&gt;')),
            ]),
            OrderedDict([
                ("tag_name", "table"),
                ("content", '<table xmlns:mml="http://www.w3.org/1998/Math/MathML"></table>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<italic>Next paragraph.</italic>'),
            ]),
        ]
        result = build.process_content_sections(content_sections, self.prefs)
        self.assertEqual(result[0].block_type, "disp-quote")
        self.assertEqual(result[0].content, '<p>Italic paragraph.</p><p>Previous paragraph.</p>')
        self.assertEqual(result[1].block_type, "table-wrap")
        self.assertEqual(result[1].content, (
            '<label>Author response Table 1.</label>'
            '<caption><title>Author response table</title></caption>'
            '<table frame="hsides" rules="groups" />'))
        self.assertEqual(result[2].block_type, "disp-quote")
        self.assertEqual(result[2].content, '<p>Next paragraph.</p>')

    def test_process_content_sections_table_disp_quote(self):
        """test for previous block is a disp-quote type"""
        content_sections = [
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<italic>Paragraph.</italic>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<bold>Author response Table 1.</bold>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", (
                    '&lt;Author response table 1 title/legend&gt;Author response table'
                    '&lt;/Author response table 1 title/legend&gt;')),
            ]),
            OrderedDict([
                ("tag_name", "table"),
                ("content", '<table xmlns:mml="http://www.w3.org/1998/Math/MathML"></table>'),
            ])
        ]
        result = build.process_content_sections(content_sections, self.prefs)
        self.assertEqual(result[0].block_type, "disp-quote")
        self.assertEqual(result[1].block_type, "table-wrap")
        self.assertEqual(result[1].content, (
            '<label>Author response Table 1.</label>'
            '<caption><title>Author response table</title></caption>'
            '<table frame="hsides" rules="groups" />'))

    def test_process_content_sections_list(self):
        content_sections = [
            OrderedDict([
                ("tag_name", "list"),
                ("content", '<list><list-item><p>Item</p></list-item></list>'),
            ])
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "list")
        self.assertEqual(result[0].attr, {})
        self.assertEqual(result[0].content, '<list-item><p>Item</p></list-item>')

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

    def test_process_content_sections_p_italic(self):
        """test case for italic p"""
        content_sections = [
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>Regular paragraph.</p>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p><italic>First quoted paragraph.</italic></p>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p><italic>Second quoted paragraph.</italic></p>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>Response paragraph.</p>'),
            ]),
        ]
        result = build.process_content_sections(content_sections, self.prefs)
        self.assertEqual(result[0].block_type, 'p')
        self.assertEqual(result[0].content, 'Regular paragraph.')
        self.assertEqual(result[1].block_type, 'disp-quote')
        self.assertEqual(result[1].attr.get('content-type'), 'editor-comment')
        self.assertEqual(
            result[1].content, '<p>First quoted paragraph.</p><p>Second quoted paragraph.</p>')
        self.assertEqual(result[2].block_type, 'p')
        self.assertEqual(result[2].content, 'Response paragraph.')


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


class TestExtractLabelTitleContent(unittest.TestCase):

    def test_simple_title(self):
        content = '<bold>Label</bold>Title. Caption.&lt;/Legend&gt;'
        label, title, caption = build.extract_label_title_content(content)
        self.assertEqual(label, 'Label')
        self.assertEqual(title, 'Title.')
        self.assertEqual(caption, 'Caption.')

    def test_organism_title(self):
        content = (
            '<bold>Label</bold>In <italic>B. subtilis</italic>, the title.'
            ' Caption.&lt;/Legend&gt;')
        label, title, caption = build.extract_label_title_content(content)
        self.assertEqual(label, 'Label')
        self.assertEqual(title, 'In <italic>B. subtilis</italic>, the title.')
        self.assertEqual(caption, 'Caption.')


class TestBuildFig(unittest.TestCase):

    def test_build_fig(self):
        content = read_fixture('author_response_fig_content.txt')
        expected = read_fixture('author_response_fig_content.py')
        fig_content = build.build_fig(content)
        self.assertEqual(fig_content, expected)

    def test_build_fig_simple_title(self):
        """example of a title with no full stop"""
        content = (
            '&lt;Author response image 1 title/legend&gt;'
            '<bold>Label</bold>Title'
            '&lt;/Author response image 1 title/legend&gt;'
            )
        expected = OrderedDict([
            ('label', 'Label'),
            ('title', 'Title'),
            ('content', None)
        ])
        fig_content = build.build_fig(content)
        self.assertEqual(fig_content, expected)


class TestBuildVideo(unittest.TestCase):

    def test_build_fig(self):
        content = read_fixture('author_response_video_content.txt')
        expected = read_fixture('author_response_video_content.py')
        # for now reusing build_fig function which satisifes the same situation
        video_content = build.build_fig(content)
        self.assertEqual(video_content, expected)


class TestBuildDispQuote(unittest.TestCase):

    def test_disp_quote_element(self):
        content = '<p>One.</p><p>Two.</p>'
        expected = b'<disp-quote><p>One.</p><p>Two.</p></disp-quote>'
        tag_content = build.disp_quote_element(content)
        tag_xml = ElementTree.tostring(tag_content)
        self.assertEqual(tag_xml, expected)


class TestBuildTableWrap(unittest.TestCase):

    def test_build_table(self):
        """example of a title"""
        content = (
            '<bold>Author response Table 1.</bold>'
            '&lt;Author response table 1 title/legend&gt;'
            'Author response table'
            '&lt;/Author response table 1 title/legend&gt;'
            '<table></table>'
            )
        expected = OrderedDict([
            ('table', '<table></table>'),
            ('label', 'Author response Table 1.'),
            ('title', 'Author response table'),
            ('content', None)
        ])
        table_content = build.build_table_wrap(content)
        self.assertEqual(table_content, expected)


class TestBuildTableWrapElement(unittest.TestCase):

    def test_table_wrap_element(self):
        label = 'Author response Table 1.'
        title = 'Author response table'
        content = 'Optional caption.'
        table = '<table></table>'
        expected = (
            b'<table-wrap><label>Author response Table 1.</label>'
            b'<caption><title>Author response table</title>'
            b'<p>Optional caption.</p></caption>'
            b'<table frame="hsides" rules="groups" /></table-wrap>'
            )
        tag_content = build.table_wrap_element(label, title, content, table)
        tag_xml = ElementTree.tostring(tag_content)
        self.assertEqual(tag_xml, expected)


class TestBuildSubArticle(unittest.TestCase):

    def setUp(self):
        self.config = parse_raw_config(raw_config('elife'))

    def test_build_sub_article_video(self):
        doi = "10.7554/eLife.00666"
        id_value = "sa2"
        article_type = "reply"
        manuscript = 666
        content = read_fixture('author_response_video_1.txt')
        section = OrderedDict([
            ('section_type', 'author_response'),
            ('content', content)
        ])
        expected_content = (
            '<label>Author response video 1.</label><caption><title>Title up to first full stop.'
            '</title><p>Caption <sup>2+</sup>.</p></caption>')
        article = build.build_sub_article(
            section, self.config, article_type, id_value, doi, manuscript)
        self.assertEqual(article.doi, doi)
        self.assertEqual(article.id, id_value)
        self.assertEqual(article.manuscript, manuscript)
        self.assertEqual(article.article_type, article_type)
        self.assertEqual(article.content_blocks[0].block_type, 'media')
        self.assertEqual(article.content_blocks[0].attr['xlink:href'], 'elife-00666-sa2-video1')
        self.assertEqual(article.content_blocks[0].content, expected_content)


class TestSetContentBlocks(unittest.TestCase):

    def test_author_response_image(self):
        content = read_fixture('author_response_image_1.txt')
        section = OrderedDict([
            ('section_type', 'author_response'),
            ('content', content)
        ])
        expected = read_fixture('author_response_image_1_content_block.py')
        article = Article()
        build.set_content_blocks(article, section)
        self.assertEqual(article.content_blocks[0].block_type, expected.block_type)
        self.assertEqual(article.content_blocks[0].content, expected.content)

    def test_author_response_video(self):
        content = read_fixture('author_response_video_1.txt')
        section = OrderedDict([
            ('section_type', 'author_response'),
            ('content', content)
        ])
        expected = read_fixture('author_response_video_1_content_block.py')
        article = Article()
        build.set_content_blocks(article, section)
        self.assertEqual(article.content_blocks[0].block_type, expected.block_type)
        self.assertEqual(article.content_blocks[0].attr, expected.attr)
        self.assertEqual(article.content_blocks[0].content, expected.content)

    def test_decision_letter_italic_disp_quote(self):
        """non-author_response will not have italic paragraphs converted to disp-quote"""
        content = '<italic>Italic paragraph.</italic>'
        section_content = '<p>%s</p>' % content
        section = OrderedDict([
            ('section_type', 'decision_letter'),
            ('content', section_content)
        ])
        expected = ContentBlock('p', content)
        article = Article()
        build.set_content_blocks(article, section)
        self.assertEqual(article.content_blocks[0].block_type, expected.block_type)
        self.assertEqual(article.content_blocks[0].content, expected.content)

    def test_author_response_italic_disp_quote(self):
        """author_response will get italic paragraphs converted to disp-quote"""
        content = 'Italic paragraph.'
        section_content = '<p><italic>%s</italic></p>' % content
        expected_content = '<p>%s</p>' % content
        section = OrderedDict([
            ('section_type', 'author_response'),
            ('content', section_content)
        ])
        expected = ContentBlock('disp-quote', expected_content, {'content-type': 'editor-comment'})
        article = Article()
        build.set_content_blocks(article, section)
        self.assertEqual(article.content_blocks[0].block_type, expected.block_type)
        self.assertEqual(article.content_blocks[0].attr, expected.attr)
        self.assertEqual(article.content_blocks[0].content, expected.content)


class TestProcessP(unittest.TestCase):

    def test_p_basic(self):
        content = '<p>Basic.</p>'
        prev = {}
        expected = ('Basic.', 'p', None, 'append', None)
        self.assertEqual(build.process_p_content(content, prev), expected)

    def test_p_add_previous(self):
        content = '<p>Basic.</p>'
        prev = {'content': 'Previous.'}
        expected = ('Basic.', 'p', None, 'add', None)
        self.assertEqual(build.process_p_content(content, prev), expected)

    def test_p_append_disp_formula(self):
        content = '<p><disp-formula></disp-formula></p>'
        prev = {'content': '<disp-formula></disp-formula>'}
        expected = ('<disp-formula></disp-formula>', 'p', None, 'append', None)
        self.assertEqual(build.process_p_content(content, prev), expected)

    def test_process_p_author_image_start(self):
        content = '&lt;Author response image 1&gt;'
        prev = {}
        expected = ('', 'p', None, 'add', 'fig')
        self.assertEqual(build.process_p_content(content, prev), expected)

    def test_process_p_author_image_end(self):
        content = 'blah blah&lt;/Author response image 1 title/legend&gt;'
        prev = {'wrap': 'fig'}
        expected = ('blah blah&lt;/Author response image 1 title/legend&gt;',
                    'p', None, 'add', None)
        self.assertEqual(build.process_p_content(content, prev), expected)

    def test_process_p_decision_image_start(self):
        content = '&lt;Decision letter image 2&gt;'
        prev = {}
        expected = ('', 'p', None, 'add', 'fig')
        self.assertEqual(build.process_p_content(content, prev), expected)

    def test_process_p_decision_image_end(self):
        content = 'blah blah&lt;/Decision letter image 2 title/legend&gt;'
        prev = {'wrap': 'fig'}
        expected = ('blah blah&lt;/Decision letter image 2 title/legend&gt;',
                    'p', None, 'add', None)
        self.assertEqual(build.process_p_content(content, prev), expected)

    def test_process_p_author_video_start(self):
        content = '&lt;Author response video 1&gt;'
        prev = {}
        expected = ('', 'p', None, 'add', 'media')
        self.assertEqual(build.process_p_content(content, prev), expected)

    def test_process_p_author_video_end(self):
        content = 'blah blah&lt;/Author response video 1 title/legend&gt;'
        prev = {'wrap': 'fig'}
        expected = ('blah blah&lt;/Author response video 1 title/legend&gt;',
                    'p', None, 'add', None)
        self.assertEqual(build.process_p_content(content, prev), expected)
