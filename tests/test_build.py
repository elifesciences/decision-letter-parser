# coding=utf-8

import unittest
from letterparser import build, parse
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
