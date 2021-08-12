# coding=utf-8

import unittest
import configparser as configparser
from letterparser import conf


def build_raw_config_for_testing(value_name, value):
    "build a config object with one value and return the defaults for testing"
    config = configparser.ConfigParser(interpolation=None)
    config["DEFAULT"][value_name] = value
    raw_config = config["DEFAULT"]
    return raw_config


class TestConf(unittest.TestCase):
    def setUp(self):
        # some values for testing
        self.boolean_value = u"True"
        self.boolean_expected = True
        self.int_value = u"42"
        self.int_expected = 42
        self.list_value = u"[1,1,2,3,5]"
        self.list_expected = [1, 1, 2, 3, 5]

    def test_load_config(self):
        "check building default configuration"
        config = conf.load_config()
        self.assertIsNotNone(config)
        self.assertGreater(len(config.sections()), 0)

    def test_raw_config_none(self):
        "check reading raw config default when the config section is None"
        config = conf.raw_config(None)
        self.assertGreater(len(config), 0)

    def test_boolean_config(self):
        "test parsing a boolean value"
        value = self.boolean_value
        value_name = u"test"
        expected = self.boolean_expected
        raw_config = build_raw_config_for_testing(value_name, value)
        self.assertEqual(conf.boolean_config(raw_config, value_name), expected)

    def test_int_config(self):
        "test parsing an int value"
        value = self.int_value
        value_name = u"test"
        expected = self.int_expected
        raw_config = build_raw_config_for_testing(value_name, value)
        self.assertEqual(conf.int_config(raw_config, value_name), expected)

    def test_list_config(self):
        "test parsing a list value"
        value = self.list_value
        value_name = u"test"
        expected = self.list_expected
        raw_config = build_raw_config_for_testing(value_name, value)
        self.assertEqual(conf.list_config(raw_config, value_name), expected)

    def test_parse_raw_config(self):
        "test parsing a raw config of all the different value types"
        # override the library values
        conf.BOOLEAN_VALUES = [u"test_boolean"]
        conf.INT_VALUES = [u"test_int"]
        conf.LIST_VALUES = [u"test_list"]
        # build a config object
        config = configparser.ConfigParser(interpolation=None)
        config["DEFAULT"][u"test_boolean"] = self.boolean_value
        config["DEFAULT"][u"test_int"] = self.int_value
        config["DEFAULT"][u"test_list"] = self.list_value
        # parse the raw config for coverage
        config_dict = conf.parse_raw_config(config["DEFAULT"])
        # assert some things
        self.assertIsNotNone(config_dict)
        self.assertEqual(config_dict.get("test_boolean"), self.boolean_expected)
        self.assertEqual(config_dict.get("test_int"), self.int_expected)
        self.assertEqual(config_dict.get("test_list"), self.list_expected)


if __name__ == "__main__":
    unittest.main()
