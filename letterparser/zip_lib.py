# coding=utf-8

import zipfile
import os


def profile_zip(file_name):
    """open the zip and get zip file info based on the filename"""
    zip_docx_info = None
    zip_asset_infos = []
    with zipfile.ZipFile(file_name, 'r') as open_zipfile:
        for zipfile_info in open_zipfile.infolist():
            # ignore files in subfolders like __MACOSX
            zipfile_file = zipfile_info.filename
            if '/' in zipfile_file:
                continue
            if zipfile_file.endswith('.docx'):
                zip_docx_info = zipfile_info
            else:
                # assume figure or video file
                zip_asset_infos.append(zipfile_info)
    # sort by file name
    zip_asset_infos = sorted(zip_asset_infos, key=lambda asset: asset.filename)
    return zip_docx_info, zip_asset_infos


def unzip_file(open_zipfile, zip_file_info, output_path):
    "read the zip_file_info from the open_zipfile and write to output_path"
    with open_zipfile.open(zip_file_info) as zip_content:
        with open(output_path, 'wb') as output_file:
            output_file.write(zip_content.read())


def unzip_zip(file_name, temp_dir):
    "unzip certain files and return the local paths"
    docx_file_name = None
    asset_file_names = []
    zip_docx_info, zip_asset_infos = profile_zip(file_name)
    # extract the files
    with zipfile.ZipFile(file_name, 'r') as open_zipfile:
        if zip_docx_info:
            docx_file_name = os.path.join(temp_dir, zip_docx_info.filename)
            unzip_file(open_zipfile, zip_docx_info, docx_file_name)
        for zip_asset_info in zip_asset_infos:
            asset_file_name = os.path.join(temp_dir, zip_asset_info.filename)
            unzip_file(open_zipfile, zip_asset_info, asset_file_name)
            asset_file_names.append(asset_file_name)
    return docx_file_name, asset_file_names
