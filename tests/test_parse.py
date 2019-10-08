import unittest
from mock import patch
import requests
import pypandoc
from letterparser import docker_lib, parse
from tests import data_path, read_fixture


class TestParse(unittest.TestCase):

    def setUp(self):
        pass

    @patch.object(pypandoc, 'convert_file')
    def test_pandoc_output_exception(self, fake_convert_file):
        fake_convert_file.side_effect = OSError()
        self.assertRaises(OSError, parse.pandoc_output('file_name'))

    @patch.object(docker_lib, 'call_pandoc')
    def test_docker_pandoc_output_exception(self, fake_call_pandoc):
        fake_call_pandoc.side_effect = requests.exceptions.ConnectionError()
        self.assertRaises(
            requests.exceptions.ConnectionError, parse.docker_pandoc_output('file_name'))

    @patch.object(parse, 'docker_pandoc_output')
    @patch.object(parse, 'pandoc_output')
    def test_parse_file_no_pandoc(self, fake_pandoc_output, fake_docker_pandoc_output):
        fake_pandoc_output.return_value = None
        fake_docker_pandoc_output.return_value = None
        output = parse.parse_file('file_name')
        self.assertIsNone(output)

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


class TestConvertBreakTags(unittest.TestCase):

    def test_convert_break_tags_simple(self):
        jats_content = '<p>One.<break /><break />Two.</p>'
        expected = '<p>One.</p><p>Two.</p>'
        result = parse.convert_break_tags(jats_content)
        self.assertEqual(result, expected)

    def test_convert_break_tags_open_italic(self):
        jats_content = '<p><italic>One</italic> <italic>two.<break /><break />3.</italic></p>'
        expected = '<p><italic>One</italic> <italic>two.</italic></p><p><italic>3.</italic></p>'
        result = parse.convert_break_tags(jats_content)
        self.assertEqual(result, expected)
