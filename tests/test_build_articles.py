# coding=utf-8

import unittest
from letterparser import build, parse
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

    def test_build_articles_fig(self):
        """edge case with fig caption and block order"""
        file_name = 'elife-00666.docx'
        jats_content = (
            '<p><bold>Author response</bold></p>'
            '<p><italic>Editor comment one.</italic></p>'
            '<p><italic>Editor comment two.</italic></p>'
            '<p>First <italic>paragraph</italic>.</p>'
            '<p>&lt;Author response image 1&gt;</p>'
            '<p>&lt;Author response image 1 title/legend&gt;<bold>Author response image 1.</bold>'
            'Title up to first full stop. Caption <sup>2+</sup> calculated using'
            '&lt;/Author response image 1 title/legend&gt;</p>'
            '<p><italic>Editor comment paragraph.</italic></p>'
            '<p>Paragraph one.</p>'
            '<p>Paragraph two.</p>')
        articles = build.build_articles(jats_content, file_name=file_name, config=self.config)
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].article_type, "reply")
        self.assertEqual(articles[0].content_blocks[0].block_type, "disp-quote")
        self.assertEqual(articles[0].content_blocks[0].content, (
            "<p>Editor comment one.</p><p>Editor comment two.</p>"))
        self.assertEqual(articles[0].content_blocks[1].block_type, "p")
        self.assertEqual(articles[0].content_blocks[1].content, (
            "First <italic>paragraph</italic>."))
        self.assertEqual(articles[0].content_blocks[2].block_type, "fig")
        self.assertEqual(articles[0].content_blocks[2].content, (
            '<label>Author response image 1.</label><caption>'
            '<title>Title up to first full stop.</title>'
            '<p>Caption <sup>2+</sup> calculated using</p></caption>'
            '<graphic mimetype="image" xlink:href="elife-00666-sa1-fig1" />'))
        self.assertEqual(articles[0].content_blocks[3].block_type, "disp-quote")
        self.assertEqual(articles[0].content_blocks[3].content, "<p>Editor comment paragraph.</p>")
        self.assertEqual(articles[0].content_blocks[4].block_type, "p")
        self.assertEqual(articles[0].content_blocks[4].content, "Paragraph one.")
        self.assertEqual(articles[0].content_blocks[5].block_type, "p")
        self.assertEqual(articles[0].content_blocks[5].content, "Paragraph two.")
