import unittest
from letterparser import parse
from letterparser.conf import raw_config, parse_raw_config
from tests import data_path, read_fixture


class TestParseList(unittest.TestCase):

    def setUp(self):
        self.config = parse_raw_config(raw_config('elife'))

    def test_raw_jats_27798(self):
        file_name = data_path('list-27798.docx')
        expected = read_fixture('list-27798_raw.xml')
        jats_content = parse.raw_jats(file_name, config=self.config)
        self.assertEqual(jats_content, expected)

    def test_raw_jats_25776(self):
        file_name = data_path('list-25776.docx')
        expected = read_fixture('list-25776_raw.xml')
        jats_content = parse.raw_jats(file_name, config=self.config)
        self.assertEqual(jats_content, expected)

    def test_raw_jats_list_types(self):
        file_name = data_path('list-types.docx')
        expected = read_fixture('list-types.xml')
        jats_content = parse.raw_jats(file_name, config=self.config)
        self.assertEqual(jats_content, expected)
