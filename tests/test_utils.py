import unittest
from ddt import ddt, data
from letterparser import utils


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
            "expected": " "
        },
        {
            "comment": "string and tag",
            "line_one": "higher precision than",
            "line_two": "<italic>σ<sub>h</sub></italic>.",
            "expected": " "
        },
        {
            "comment": "both have tags",
            "line_one": "<alternatives>",
            "line_two": "<tex-math><![CDATA[n]]></tex-math>",
            "expected": ""
        }
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
            "expected": "K<sub>M</sub> of chloride conduction between 300-400 mM"
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
