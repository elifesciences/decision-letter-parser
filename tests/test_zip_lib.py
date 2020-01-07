# coding=utf-8

import unittest
import os
from ddt import ddt, data
from tests import data_path
from letterparser.zip_lib import profile_zip, unzip_zip

@ddt
class TestZip(unittest.TestCase):

    @data(
        'elife-39122.zip',
        'elife-39122_with_subfolder.zip',
    )
    def test_profile_zip(self, zip_file):
        "test parsing of zip file to find the docx and image file names"
        expected_docx = 'elife-39122.docx'
        expected_assets = ['elife-39122-sa2-fig1.jpg', 'elife-39122-sa2-fig2.jpg']
        docx, assets = profile_zip(data_path(zip_file))
        docx_file_name = docx.filename
        asset_file_names = [asset.filename for asset in assets]
        self.assertEqual(docx.filename, expected_docx,
                         'file_name {file_name}, expected {expected}, got {output}'.format(
                             file_name=zip_file, expected=expected_docx, output=docx_file_name))
        self.assertEqual(asset_file_names, expected_assets,
                         'file_name {file_name}, expected {expected}, got {output}"'.format(
                             file_name=zip_file, expected=expected_assets, output=asset_file_names))

    def test_unzip_zip(self):
        "test parsing of zip file to find the docx and image file names"
        zip_file = 'elife-39122.zip'
        temp_dir = 'tmp'
        docx, assets = unzip_zip(data_path(zip_file), 'tmp')
        expected_docx = os.path.join(temp_dir, 'elife-39122.docx')
        expected_assets = [
            os.path.join(temp_dir, 'elife-39122-sa2-fig1.jpg'),
            os.path.join(temp_dir, 'elife-39122-sa2-fig2.jpg')]
        self.assertEqual(docx, expected_docx,
                         'expected {expected}, got {output}'.format(
                             expected=expected_docx, output=docx))
        self.assertEqual(assets, expected_assets,
                         'expected {expected}, got {output}'.format(
                             expected=expected_assets, output=assets))
