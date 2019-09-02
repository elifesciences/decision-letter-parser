import unittest
from letterparser import parse
from tests import data_path, read_fixture


class TestStrikeThrough(unittest.TestCase):

    def setUp(self):
        pass

    def test_raw_jats(self):
        file_name = data_path('strike-through-34497.docx')
        expected = read_fixture('strike-through-34497_raw.xml')
        jats_content = parse.raw_jats(file_name)
        self.assertEqual(jats_content, expected)

    def test_best_jats(self):
        file_name = data_path('strike-through-34497.docx')
        expected = read_fixture('strike-through-34497_best.xml')
        jats_content = parse.best_jats(file_name)
        self.assertEqual(jats_content, expected)
