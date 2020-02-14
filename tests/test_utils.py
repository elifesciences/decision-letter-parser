# coding=utf-8

import unittest
from ddt import ddt, data
from letterparser import utils


@ddt
class TestRemoveStrike(unittest.TestCase):

    @data(
        {
            "comment": "None value",
            "string": None,
            "expected": ""
        },
        {
            "comment": "Basic string",
            "string": "string",
            "expected": "string"
        },
        {
            "comment": "One strike tag",
            "string": "This is <strike>not</strike> that.",
            "expected": "This is that."
        },
        {
            "comment": "Two strike tags",
            "string": "This is <strike>really</strike> <strike>not</strike> that.",
            "expected": "This is that."
        },
        {
            "comment": "Strike tag around italic",
            "string": "This is <strike><italic>really</italic></strike> that.",
            "expected": "This is that."
        },
        {
            "comment": "Strike tag at end of sentence",
            "string": "This is really <strike>the end</strike>.",
            "expected": "This is really."
        },
        {
            "comment": "Strike tag at end of sentence",
            "string": "<strike>Hmm...</strike> Just testing.",
            "expected": "Just testing."
        },
        )
    def test_remove_strike(self, test_data):
        new_string = utils.remove_strike(test_data.get("string"))
        self.assertEqual(
            new_string, test_data.get("expected"),
            "{value} does not equal {expected}, scenario {comment}".format(
                value=new_string,
                expected=test_data.get("expected"),
                comment=test_data.get("comment")))


@ddt
class TestNewLineReplaceWith(unittest.TestCase):

    @data(
        {
            "comment": "None values",
            "line_one": None,
            "line_two": None,
            "expected": ""
        },
        {
            "comment": "strings only",
            "line_one": "one",
            "line_two": "two",
            "expected": "</p><p>"
        },
        {
            "comment": "string and tag",
            "line_one": "higher precision than",
            "line_two": "<italic>σ<sub>h</sub></italic>.",
            "expected": ""
        },
        {
            "comment": "both have tags",
            "line_one": "<alternatives>",
            "line_two": "<tex-math><![CDATA[n]]></tex-math>",
            "expected": ""
        },
        {
            "comment": "italic paragraph with a trailing space",
            "line_one": "<p><italic> ",
            "line_two": "1) I am not sure...",
            "expected": ""
        },
        {
            "comment": "continued italic tag",
            "line_one": "... rectification observed. ",
            "line_two": "</italic></p>",
            "expected": ""
        },
        {
            "comment": "paragraph break",
            "line_one": "</italic></p>",
            "line_two": "<p>In our analysis...",
            "expected": ""
        },
        )
    def test_new_line_replace_with(self, test_data):
        replace_with = utils.new_line_replace_with(
            test_data.get("line_one"), test_data.get("line_two"))
        self.assertEqual(
            replace_with, test_data.get("expected"),
            "{value} does not equal {expected}, scenario {comment}".format(
                value=replace_with,
                expected=test_data.get("expected"),
                comment=test_data.get("comment")))


@ddt
class TestCollapseNewlines(unittest.TestCase):

    @data(
        {
            "comment": "None value",
            "string": None,
            "expected": None
        },
        {
            "comment": "No tags around new line character",
            "string": "K<sub>M</sub> of chloride\nconduction between 300-400 mM",
            "expected": "K<sub>M</sub> of chloride</p><p>conduction between 300-400 mM"
        },
        {
            "comment": "Tags before and after new line character",
            "string": "were calculated using</p>\n<p><disp-formula><alternatives>\n<tex-math>",
            "expected": "were calculated using</p><p><disp-formula><alternatives><tex-math>"
        }
        )
    def test_collapse_newlines(self, test_data):
        new_string = utils.collapse_newlines(test_data.get("string"))
        self.assertEqual(
            new_string, test_data.get("expected"),
            "{value} does not equal {expected}, scenario {comment}".format(
                value=new_string,
                expected=test_data.get("expected"),
                comment=test_data.get("comment")))


@ddt
class TestCleanPortion(unittest.TestCase):

    @data(
        {
            "comment": "None value",
            "root_tag": "root",
            "string": None,
            "expected": ""
        },
        {
            "comment": "Plain string",
            "root_tag": "root",
            "string": "",
            "expected": ""
        },
        {
            "comment": "root tag at start of string",
            "root_tag": "root",
            "string": "<root><p>Text</p>",
            "expected": "<p>Text</p>"
        },
        {
            "comment": "root tag at end of string",
            "root_tag": "root",
            "string": "<p>Text</p></root>",
            "expected": "<p>Text</p>"
        }
        )
    def test_collapse_newlines(self, test_data):
        new_string = utils.clean_portion(test_data.get("string"), test_data.get("root_tag"))
        self.assertEqual(
            new_string, test_data.get("expected"),
            "{value} does not equal {expected}, scenario {comment}".format(
                value=new_string,
                expected=test_data.get("expected"),
                comment=test_data.get("comment")))


class TestFileNameFunctions(unittest.TestCase):

    def setUp(self):
        self.file_name = 'folder/file.txt'

    def test_get_file_name_path(self):
        expected = 'folder'
        self.assertEqual(utils.get_file_name_path(self.file_name), expected)

    def test_get_file_name_file(self):
        expected = 'file.txt'
        self.assertEqual(utils.get_file_name_file(self.file_name), expected)


@ddt
class TestManuscriptFromFileName(unittest.TestCase):

    @data(
        {
            "file_name": None,
            "expected": None
        },
        {
            "file_name": "Dutzler 39122 edit.docx",
            "expected": "39122"
        },
        {
            "file_name": "folder/Dutzler 39122 edit.docx",
            "expected": "39122"
        },
        {
            "file_name": "folder/elife-00666.docx",
            "expected": "666"
        },
        {
            "file_name": "folder/elife-NaN.docx",
            "expected": None
        },
        )
    def test_manuscript_from_file_name(self, test_data):
        manuscript = utils.manuscript_from_file_name(test_data.get("file_name"))
        self.assertEqual(manuscript, test_data.get("expected"))


class TestOpenTag(unittest.TestCase):

    def test_open_tag(self):
        tag_name = 'italic'
        expected = '<italic>'
        self.assertEqual(utils.open_tag(tag_name), expected)

    def test_open_tag_with_attr(self):
        tag_name = 'xref'
        attr = {'id': 'sa2fig1', 'ref-type': 'fig'}
        expected = '<xref id="sa2fig1" ref-type="fig">'
        self.assertEqual(utils.open_tag(tag_name, attr), expected)
