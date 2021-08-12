# coding=utf-8

import unittest
from letterparser import generate
from letterparser.conf import raw_config, parse_raw_config
from tests import data_path, read_fixture


class TestGenerateFromFile(unittest.TestCase):
    def test_generate_xml_from_file_docx(self):
        """simple test for code coverage"""
        file_name = data_path("elife-99999.docx")
        config = parse_raw_config(raw_config("elife"))
        expected = read_fixture("elife-99999.xml", mode="rb")
        pretty_xml = generate.generate_xml_from_file(
            file_name, pretty=True, indent="    ", config=config
        )
        self.assertEqual(pretty_xml, expected)
