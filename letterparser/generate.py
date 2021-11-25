# coding=utf-8

import os
import re
from collections import OrderedDict
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from letterparser import build, parse, utils, zip_lib


# max level of recursion adding content blocks supported
MAX_LEVEL = 5


def set_if_value(element, name, value):
    """set Element attribute if the value is not empty"""
    if value:
        element.set(name, value)


def generate_xml_from_file(
    file_name, root_tag="root", pretty=False, indent="", config=None, temp_dir="tmp"
):
    """from file input, generate from zip or docx based on the file extension"""
    if re.match(r".*\.[Zz][Ii][Pp]$", file_name):
        return generate_xml_from_zip(
            file_name,
            root_tag=root_tag,
            pretty=pretty,
            indent=indent,
            config=config,
            temp_dir=temp_dir,
        )
    return generate_xml_from_docx(
        file_name,
        root_tag=root_tag,
        pretty=pretty,
        indent=indent,
        config=config,
        temp_dir=temp_dir,
    )


def generate_xml_from_zip(
    file_name, root_tag="root", pretty=False, indent="", config=None, temp_dir="tmp"
):
    """generate JATS output from zip file"""
    docx_file_name, asset_file_names = zip_lib.unzip_zip(file_name, temp_dir)
    return generate_xml_from_docx(
        docx_file_name,
        root_tag=root_tag,
        pretty=pretty,
        indent=indent,
        config=config,
        temp_dir=temp_dir,
    )


def generate_xml_from_docx(
    file_name, root_tag="root", pretty=False, indent="", config=None, temp_dir="tmp"
):
    """generate JATS output from docx file_name"""
    articles = docx_to_articles(file_name, root_tag, config, temp_dir)
    jats_xml = generate(articles, root_tag, temp_dir)
    return output_xml(jats_xml, pretty, indent)


def docx_to_articles(file_name, root_tag="root", config=None, temp_dir="tmp"):
    """convert the docx file to Article objects"""
    jats_content = parse.best_jats(
        file_name, root_tag, config=config, temp_dir=temp_dir
    )
    return build.build_articles(jats_content, file_name=file_name, config=config)


def generate(articles, root_tag="root", temp_dir="tmp"):
    """from jats_content generate final JATS output"""
    # Create the root XML node
    root = Element(root_tag)
    # set namespaces
    root.set("xmlns:ali", "http://www.niso.org/schemas/ali/1.0/")
    root.set("xmlns:mml", "http://www.w3.org/1998/Math/MathML")
    root.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
    for article in articles:
        sub_article_tag = SubElement(root, "sub-article")
        set_if_value(sub_article_tag, "article-type", article.article_type)
        set_if_value(sub_article_tag, "id", article.id)
        set_front_stub(sub_article_tag, article)
        set_body(sub_article_tag, article)
        # set tag id attributes per sub-article
        set_id_attributes(sub_article_tag, "mml:math", article.id)
        set_id_attributes(sub_article_tag, "disp-formula", article.id)
        set_id_attributes(sub_article_tag, "fig", article.id)
        set_id_attributes(sub_article_tag, "table-wrap", article.id)
        set_id_attributes(sub_article_tag, "media", article.id)
        # highlight mentions of fig, media, table with an xref tag
        asset_xref_tags(sub_article_tag)
        # rename asset files in the XML
        rename_assets(root, temp_dir)
    return root


def rename_assets(root, temp_dir="tmp"):
    """rename xlink:link values if matches the file names in the temp_dir"""
    # profile the image file names in the tmp folder
    file_names = sorted(os.listdir(temp_dir))
    file_name_map = OrderedDict()
    for file_name in file_names:
        file_name_name = utils.get_file_name_file(file_name).split(".")[0]
        if file_name_name:
            file_name_map[file_name_name] = file_name
    # search for tags and rewrite the xlink:href values
    xpath_list = [".//graphic", ".//media"]
    for xpath in xpath_list:
        for tag in root.findall(xpath):
            href = tag.get("xlink:href")
            if href and href in file_name_map:
                tag.set("xlink:href", file_name_map.get(href))


def id_prefix(tag_name):
    """return the id attribute prefix for the tag name"""
    id_prefix_map = {
        "mml:math": "m",
        "disp-formula": "equ",
        "fig": "fig",
        "table-wrap": "table",
        "media": "video",
    }
    return str(id_prefix_map.get(tag_name))


def set_id_attributes(root, tag_name, article_id):
    """set the id attribute of tags"""
    i = 1
    for tag in root.iter(tag_name):
        if "id" not in tag.attrib:
            tag.set("id", "%s%s%s" % (article_id, id_prefix(tag_name), i))
            i += 1


def set_front_stub(parent, article):
    front_stub_tag = SubElement(parent, "front-stub")
    if article.doi:
        doi_tag = SubElement(front_stub_tag, "article-id")
        doi_tag.set("pub-id-type", "doi")
        doi_tag.text = article.doi
    if article.title:
        title_group_tag = SubElement(front_stub_tag, "title-group")
        article_title_tag = SubElement(title_group_tag, "article-title")
        article_title_tag.text = article.title
    # add related-object link to Editor's evaluation
    related_object_num = 1
    for related_material in article.related_articles:
        if related_material.ext_link_type and related_material.xlink_href:
            related_object_tag = SubElement(front_stub_tag, "related-object")
            related_object_tag.set("id", "%sro%s" % (article.id, related_object_num))
            related_object_tag.set("object-id-type", "id")
            related_object_tag.set(
                "object-id", utils.object_id_from_uri(related_material.xlink_href)
            )
            related_object_tag.set("link-type", related_material.ext_link_type)
            related_object_tag.set("xlink:href", related_material.xlink_href)
            related_object_num += 1


def set_body(parent, article):
    body_tag = SubElement(parent, "body")
    set_content_blocks(body_tag, article.content_blocks)
    return body_tag


def set_content_blocks(parent, content_blocks, level=1):
    if level > MAX_LEVEL:
        raise Exception("Maximum level of nested content blocks reached")
    for block in content_blocks:
        block_tag = None
        if block.block_type in [
            "boxed-text",
            "disp-formula",
            "disp-quote",
            "fig",
            "list",
            "media",
            "p",
            "table-wrap",
        ]:
            # retain standard tag attributes as well as any specific ones from the block object
            if block.content:
                utils.append_to_parent_tag(
                    parent,
                    block.block_type,
                    block.content,
                    utils.XML_NAMESPACE_MAP,
                    attributes=block.attr_names(),
                    attributes_text=block.attr_string(),
                )
                block_tag = parent[-1]
            else:
                # add empty tags too
                block_tag = SubElement(parent, block.block_type)
                block_tag.text = block.content
                for key, value in block.attr.items():
                    block_tag.set(key, value)
        if block_tag is not None and block.content_blocks:
            # recursion
            set_content_blocks(block_tag, block.content_blocks, level + 1)


def labels(root):
    """find label values from assets"""
    asset_labels = []
    name_type_map = OrderedDict(
        [("fig", "fig"), ("media", "video"), ("table-wrap", "table")]
    )
    for tag_name in list(name_type_map):
        for block_tag in root.findall(".//" + tag_name):
            label_tags = block_tag.findall(".//label")
            if block_tag.get("id") and label_tags:
                asset_label = OrderedDict()
                asset_label["id"] = block_tag.get("id")
                asset_label["type"] = name_type_map.get(tag_name)
                asset_label["text"] = label_tags[0].text
                asset_labels.append(asset_label)
    return asset_labels


def asset_xref_tags(root):
    """
    wrap mentions of asset labels in paragraphs with an <xref> tag
    method to replace tags in an ElementTree it will remove the old one and insert the new
    which requires to know the p tag parent and index of the p tag inside that parent
    """
    asset_labels = labels(root)
    # strip full stop at end of label if present
    for label in asset_labels:
        if label.get("text"):
            label["text"] = label.get("text").rstrip(".")
    # look for tags that have a p tag in them
    for p_tag_parent in root.findall(".//p/.."):
        p_tag_parent_asset_xref(p_tag_parent, asset_labels)


def p_tag_parent_asset_xref(p_tag_parent, asset_labels):
    # loop through the p tags in this parent tag, keeping track of the p tag index
    for tag_index, child_tag in enumerate(p_tag_parent.iterfind("*")):
        if not child_tag.tag == "p":
            continue
        tag_string = build.element_to_string(child_tag)
        modified_tag_string = xml_string_asset_xref(tag_string, asset_labels)

        if tag_string != modified_tag_string:
            # add namespaces before parsing again
            p_tag_string = "<p %s>" % utils.reparsing_namespaces(
                utils.XML_NAMESPACE_MAP
            )
            modified_tag_string = re.sub(
                r"^<p>", p_tag_string, str(modified_tag_string)
            )
            new_p_tag = ElementTree.fromstring(modified_tag_string)
            # remove old tag
            p_tag_parent.remove(child_tag)
            # insert the new tag
            p_tag_parent.insert(tag_index, new_p_tag)


def profile_asset_labels(labels):
    "check if label term is unique or whether another label starts with it"
    labels_data = []
    for label in labels:
        labels_start_with = [
            search_label
            for search_label in labels
            if search_label.startswith(label) and search_label != label
        ]
        data = OrderedDict([("label", label), ("unique", not bool(labels_start_with))])
        labels_data.append(data)
    return labels_data


def sort_labels(labels_data):
    "sort asset labels with unique ones first then the rest"
    unique_labels = [
        match_group for match_group in labels_data if match_group.get("unique")
    ]
    non_unique_labels = [
        match_group for match_group in labels_data if not match_group.get("unique")
    ]
    return unique_labels + non_unique_labels


def label_match_pattern(xref_open_tag, label_text):
    "regular expression to find mentions of a label in text that are not already xref tagged"
    return r"(?<!%s)(%s[-a-zA-z]*)" % (xref_open_tag, label_text)


def label_matches(xml_string, xref_open_tag, label_text):
    "get list of labels in text that are not already preceeded by the xref tag"
    return re.findall(label_match_pattern(xref_open_tag, label_text), xml_string)


def xml_string_asset_xref(xml_string, asset_labels):
    """
    Wrap occurences of each asset label in the XML string with an <xref> tag
    The label in the text can also include a specific panel name, e.g.
    a label of "Author response image 1", when adding <xref> tags to the text it can result in
    all of these example possibilites
    <xref ref-type="fig" rid="sa2fig1">Author response image 1</xref>
    <xref ref-type="fig" rid="sa2fig1">Author response image 1B</xref>
    <xref ref-type="fig" rid="sa2fig1">Author response image 1A-F</xref>
    <xref ref-type="fig" rid="sa2fig1">Author response image 1A</xref> and B
    """
    for asset_label in asset_labels:
        if asset_label.get("text") and asset_label.get("text") in str(xml_string):
            attr = {"rid": asset_label.get("id"), "ref-type": asset_label.get("type")}
            xref_open_tag = utils.open_tag("xref", attr)
            xref_close_tag = utils.close_tag("xref")
            # look for label in the text but not preceeded by the xref open tag we want to add
            label_match_groups = label_matches(
                xml_string, xref_open_tag, asset_label.get("text")
            )
            labels = sort_labels(profile_asset_labels(label_match_groups))

            for label in labels:
                safe_match_pattern = r"(?<!%s)%s" % (xref_open_tag, label.get("label"))
                replacement_pattern = r"%s%s%s" % (
                    xref_open_tag,
                    label.get("label"),
                    xref_close_tag,
                )
                xml_string = re.sub(safe_match_pattern, replacement_pattern, xml_string)

    return xml_string


def output_xml(root, pretty=False, indent=""):
    """output root XML Element to a string"""
    encoding = "utf-8"
    rough_string = ElementTree.tostring(root, encoding)
    rough_string = utils.xml_string_fix_namespaces(rough_string, root.tag)
    reparsed = minidom.parseString(rough_string)

    if pretty is True:
        return reparsed.toprettyxml(indent, encoding=encoding)
    return reparsed.toxml(encoding=encoding)


def output_xml_escaped(root, pretty=False, indent=""):
    """output root XML Element to a string with character entities replaced"""
    return utils.replace_character_entities(output_xml(root, pretty, indent))


def output_xml_modified(root, pretty=False, indent=""):
    """output root XML Element to a string with many modified tags and characters"""
    xml_string = output_xml(root, pretty, indent)
    xml_string = utils.replace_character_entities(xml_string)
    xml_string = utils.replace_unicode_entities(xml_string)
    xml_string = utils.replace_math_mml_tags(xml_string)
    return xml_string
