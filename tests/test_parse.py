import unittest
from letterparser import parse
from tests import data_path, read_fixture


class TestParse(unittest.TestCase):

    def setUp(self):
        pass

    def test_raw_jats(self):
        file_name = data_path('Dutzler 39122 edit.docx')
        expected = read_fixture('raw_jats_dutzler_39122.xml')
        jats_content = parse.raw_jats(file_name)
        self.assertEqual(jats_content, expected)

    def test_clean_jats(self):
        file_name = data_path('Dutzler 39122 edit.docx')
        expected = read_fixture('clean_jats_dutzler_39122.xml')
        jats_content = parse.clean_jats(file_name)
        parse.sections(jats_content)
        self.assertEqual(jats_content, expected)

    def test_best_jats(self):
        file_name = data_path('Dutzler 39122 edit.docx')
        expected = read_fixture('best_jats_dutzler_39122.xml')
        jats_content = parse.best_jats(file_name)
        self.assertEqual(jats_content, expected)

    def test_sections(self):
        file_name = data_path('Dutzler 39122 edit.docx')
        expected = read_fixture('dutzler_39122_sections.py')
        jats_content = parse.best_jats(file_name)
        sections = parse.sections(jats_content)
        self.assertEqual(sections, expected)
