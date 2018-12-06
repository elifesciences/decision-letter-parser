import unittest
from letterparser import parse

class TestParse(unittest.TestCase):

    def setUp(self):
        pass

    def test_dummy(self):
        self.assertTrue(parse.dummy())


if __name__ == '__main__':
    unittest.main()