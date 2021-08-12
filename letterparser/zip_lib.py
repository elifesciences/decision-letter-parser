# coding=utf-8

import zipfile
import os
import shutil
from letterparser import utils


def profile_zip(file_name):
    """open the zip and get zip file info based on the filename"""
    zip_docx_info = None
    zip_asset_infos = []
    with zipfile.ZipFile(file_name, "r") as open_zipfile:
        for zipfile_info in open_zipfile.infolist():
            # ignore files in subfolders like __MACOSX
            zipfile_file = zipfile_info.filename
            if "/" in zipfile_file:
                continue
            if zipfile_file.endswith(".docx"):
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
        with open(output_path, "wb") as output_file:
            output_file.write(zip_content.read())


def unzip_zip(file_name, temp_dir):
    "unzip certain files and return the local paths"
    docx_file_name = None
    asset_file_names = []
    zip_docx_info, zip_asset_infos = profile_zip(file_name)
    # extract the files
    with zipfile.ZipFile(file_name, "r") as open_zipfile:
        if zip_docx_info:
            docx_file_name = os.path.join(temp_dir, zip_docx_info.filename)
            unzip_file(open_zipfile, zip_docx_info, docx_file_name)
        for zip_asset_info in zip_asset_infos:
            asset_file_name = os.path.join(temp_dir, zip_asset_info.filename)
            unzip_file(open_zipfile, zip_asset_info, asset_file_name)
            asset_file_names.append(asset_file_name)
    return docx_file_name, asset_file_names


def fix_complex_scripts_styles(file_name, temp_dir="tmp"):
    """copy the docx file and fix complex scripts style tags"""
    new_zip_file_name = os.path.join(temp_dir, "temp.docx")
    new_file_name = os.path.join(temp_dir, utils.get_file_name_file(file_name))
    # create a new zip file with altered word/document.xml file contents
    with zipfile.ZipFile(
        file_name, "r", zipfile.ZIP_DEFLATED, allowZip64=True
    ) as open_zip:
        with zipfile.ZipFile(
            new_zip_file_name, "w", zipfile.ZIP_DEFLATED, allowZip64=True
        ) as new_open_zip:
            complex_scripts_styles_rewrite(open_zip, new_open_zip)
    # copy the new zip overtop of existing docx, if present
    shutil.move(new_zip_file_name, new_file_name)
    return new_file_name


def complex_scripts_styles_rewrite(from_zip, to_zip):
    """
    given two open zipfile.Zipfile objects from docx files,
    read items from from_zip,
    write them to to_zip and remove complex script styles from the document.xml file
    """
    for zip_file_name in from_zip.namelist():
        if zip_file_name == "word/document.xml":
            with from_zip.open(zip_file_name) as open_file:
                document_xml = open_file.read()
                document_xml = utils.remove_complex_scripts_styles(document_xml)
                # write the altered string to the new zip file
                to_zip.writestr(zip_file_name, document_xml)
        else:
            # copy the file into the new zip
            to_zip.writestr(zip_file_name, from_zip.read(zip_file_name))
