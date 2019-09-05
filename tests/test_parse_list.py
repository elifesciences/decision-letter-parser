import unittest
from letterparser import parse
from tests import data_path, read_fixture


class TestParseList(unittest.TestCase):

    def setUp(self):
        pass

    def test_raw_jats_27798(self):
        file_name = data_path('list-27798.docx')
        expected = read_fixture('list-27798_raw.xml')
        jats_content = parse.raw_jats(file_name)
        self.assertEqual(jats_content, expected)

    def test_raw_jats_25776(self):
        file_name = data_path('list-25776.docx')
        expected = read_fixture('list-25776_raw.xml')
        jats_content = parse.raw_jats(file_name)
        self.assertEqual(jats_content, expected)
