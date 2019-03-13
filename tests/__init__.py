"""helper functions for running tests"""
import os


BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))


def read_fixture(filename):
    """read a file from the fixtures directory"""
    with open(data_path(filename), 'r') as file_fp:
        return file_fp.read()


def data_path(file_name):
    """path for a file in the test_data directory"""
    return os.path.join(BASE_DIR, 'tests', 'test_data', file_name)
