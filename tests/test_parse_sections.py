import unittest
from letterparser import parse
from letterparser.conf import raw_config, parse_raw_config
from tests import data_path, read_fixture


class TestParseSections(unittest.TestCase):
    def setUp(self):
        self.config = parse_raw_config(raw_config("elife"))

    def test_sections(self):
        file_name = data_path("sections.docx")
        expected = read_fixture("sections_sections.py")
        jats_content = parse.best_jats(file_name, config=self.config)
        sections = parse.sections(jats_content)
        self.assertEqual(sections, expected)
