# coding=utf-8

import unittest
from ddt import ddt, data
from letterparser import build


@ddt
class TestMatchPatterns(unittest.TestCase):

    @data(
        {
            "content": "",
            "expected": False
        },
        {
            "content": "&lt;Author response image 1&gt;",
            "expected": True
        },
        {
            "content": "content &lt;Author response image 1&gt;",
            "expected": False
        },
        {
            "content": "&lt;Decision letter image 666&gt;",
            "expected": True
        },
    )
    def test_match_fig_content_start(self, test_data):
        self.assertEqual(
            build.match_fig_content_start(test_data.get('content')),
            test_data.get('expected'))

    @data(
        {
            "content": "",
            "expected": False
        },
        {
            "content": "&lt;Author response image 1 title/legend&gt;",
            "expected": True
        },
        {
            "content": "content &lt;Author response image 1 title/legend&gt;",
            "expected": False
        },
        {
            "content": "&lt;Decision letter image 666 title/legend&gt;",
            "expected": True
        },
    )
    def test_match_fig_content_title_start(self, test_data):
        self.assertEqual(
            build.match_fig_content_title_start(test_data.get('content')),
            test_data.get('expected'))
