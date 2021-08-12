import unittest
from tests import fixture_module_name, fixture_file, read_fixture


class TestTests(unittest.TestCase):

    def test_fixture_file_none(self):
        self.assertIsNone(fixture_file(None))

    def test_fixture_module_name(self):
        filename = 'test_module'
        expected = 'tests.fixtures.test_module'
        self.assertEqual(fixture_module_name(filename), expected)

    def test_read_fixture(self):
        filename = 'true.py'
        self.assertTrue(read_fixture(filename))
