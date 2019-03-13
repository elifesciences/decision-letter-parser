import unittest
from letterparser import parse
from tests import data_path, read_fixture


class TestParse(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_raw_jats(self):
        file_name = data_path('Dutzler 39122 edit.docx')
        expected = read_fixture('raw_jats_dutzler_39122.xml')
        jats_content = parse.get_raw_jats(file_name)
        self.assertEqual(jats_content, expected)
