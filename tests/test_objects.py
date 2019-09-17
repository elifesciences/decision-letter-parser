# coding=utf-8

import unittest
from letterparser.objects import ContentBlock


class TestContentBlock(unittest.TestCase):

    def test_attr(self):
        """test attributes function"""
        content_block = ContentBlock("disp-quote")
        content_block.attr["content-type"] = "editor-comment"
        content_block.attr["escaped"] = "\""
        self.assertEqual(sorted(content_block.attr_names()), ["content-type", "escaped"])
        self.assertEqual(
            content_block.attr_string(), ' content-type="editor-comment" escaped="&quot;"')
