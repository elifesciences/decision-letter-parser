import unittest
from letterparser import parse
from letterparser.conf import raw_config, parse_raw_config
from tests import data_path, read_fixture


class TestParseTable(unittest.TestCase):
    def setUp(self):
        self.config = parse_raw_config(raw_config("elife"))

    def test_raw_jats_35684(self):
        file_name = data_path("table-35684.docx")
        expected = read_fixture("table-35684_raw.xml")
        jats_content = parse.raw_jats(file_name, config=self.config)
        self.assertEqual(jats_content, expected)

    def test_raw_jats_43333(self):
        file_name = data_path("table-43333.docx")
        expected = read_fixture("table-43333_raw.xml")
        jats_content = parse.raw_jats(file_name, config=self.config)
        self.assertEqual(jats_content, expected)

    def test_raw_jats_42299(self):
        file_name = data_path("table-42299.docx")
        expected = read_fixture("table-42299_raw.xml")
        jats_content = parse.raw_jats(file_name, config=self.config)
        self.assertEqual(jats_content, expected)
