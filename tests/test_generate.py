# coding=utf-8

import unittest
from collections import OrderedDict
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from ddt import ddt, data
from elifearticle.article import ContentBlock
from letterparser import generate
from letterparser.conf import raw_config, parse_raw_config
from tests import data_path, helpers, read_fixture


def simple_decision_letter():
    sub_article = helpers.base_decision_letter()
    preamble_block = ContentBlock("boxed-text")
    preamble_block.content_blocks.append(ContentBlock("p", "Preamble"))
    sub_article.content_blocks.append(preamble_block)
    sub_article.content_blocks.append(ContentBlock("p", (
        "Thank you for submitting your article \"ZZ9 Plural Z α\" to <italic>eLife</italic>.")))
    return sub_article


def simple_author_response():
    sub_article = helpers.base_author_response()
    sub_article.content_blocks.append(ContentBlock("p", "Essential revisions:"))
    disp_quote_block = ContentBlock("disp-quote")
    disp_quote_block.attr["content-type"] = "editor-comment"
    disp_quote_block.content_blocks.append(ContentBlock(
        "p", "1) I am not sure that I understand ...."))
    sub_article.content_blocks.append(disp_quote_block)
    return sub_article


class TestGenerateOutputXML(unittest.TestCase):

    def test_output_xml(self):
        """test non-pretty output of a simple ElementTree object"""
        root = Element("root")
        expected = b'<?xml version="1.0" encoding="utf-8"?><root/>'
        self.assertEqual(generate.output_xml(root), expected)

    def test_output_xml_character_entities(self):
        """test non-pretty output of a simple ElementTree object"""
        root = Element("root")
        root.text = '&<>"'
        expected = b'<?xml version="1.0" encoding="utf-8"?><root>&amp;&lt;&gt;&quot;</root>'
        self.assertEqual(generate.output_xml(root), expected)


class TestGenerateOutputXMLEscaped(unittest.TestCase):

    def test_output_xml(self):
        """test non-pretty output of a simple ElementTree object"""
        root = Element("root")
        expected = b'<?xml version="1.0" encoding="utf-8"?><root/>'
        self.assertEqual(generate.output_xml_escaped(root), expected)

    def test_output_xml_character_entities(self):
        """test non-pretty output of a simple ElementTree object"""
        root = Element("root")
        root.text = '&<>"'
        expected = (
            b'<?xml version="1.0" encoding="utf-8"?><root>'
            b'&#x0026;&#x003C;&#x003E;&#x0022;</root>')
        self.assertEqual(generate.output_xml_escaped(root), expected)


class TestGenerate(unittest.TestCase):

    def test_generate_simple(self):
        """test generating a simple article"""
        articles = [simple_decision_letter(), simple_author_response()]
        root = generate.generate(articles)
        pretty_xml = generate.output_xml(root, pretty=True, indent="    ")
        expected = read_fixture("generate_simple.xml", mode="rb")
        self.assertEqual(pretty_xml, expected)


class TestGenerateFromFile(unittest.TestCase):

    def test_generate_xml_from_file_zip(self):
        """simple test for code coverage"""
        file_name = data_path('elife-39122.zip')
        config = parse_raw_config(raw_config('elife'))
        pretty_xml = generate.generate_xml_from_file(
            file_name, pretty=True, indent="    ", config=config)
        self.assertIsNotNone(pretty_xml)

    def test_generate_xml_from_file_docx(self):
        """simple test for code coverage"""
        file_name = data_path('Dutzler 39122 edit.docx')
        config = parse_raw_config(raw_config('elife'))
        pretty_xml = generate.generate_xml_from_file(
            file_name, pretty=True, indent="    ", config=config)
        self.assertIsNotNone(pretty_xml)


class TestGenerateFromZip(unittest.TestCase):

    def test_generate_xml_from_zip(self):
        """simple test for code coverage"""
        file_name = data_path('elife-39122.zip')
        config = parse_raw_config(raw_config('elife'))
        pretty_xml = generate.generate_xml_from_zip(
            file_name, pretty=True, indent="    ", config=config)
        self.assertIsNotNone(pretty_xml)


class TestGenerateKitchenSinkZip(unittest.TestCase):

    def test_generate_xml_from_zip(self):
        """simple test for code coverage"""
        file_name = data_path('elife-00666.zip')
        xml_string = read_fixture('elife-00666.xml', mode="rb")
        config = parse_raw_config(raw_config('elife'))
        pretty_xml = generate.generate_xml_from_zip(
            file_name, pretty=True, indent="    ", config=config)
        self.assertEqual(pretty_xml, xml_string)


class TestGenerateFromDocx(unittest.TestCase):

    def test_generate_xml_from_docx(self):
        """simple test for code coverage"""
        file_name = data_path('Dutzler 39122 edit.docx')
        config = parse_raw_config(raw_config('elife'))
        pretty_xml = generate.generate_xml_from_docx(
            file_name, pretty=True, indent="    ", config=config)
        self.assertIsNotNone(pretty_xml)


class TestGenerateArticlesForTables(unittest.TestCase):

    def test_generate_table_35684(self):
        file_name = data_path('table-35684.docx')
        config = parse_raw_config(raw_config('elife'))
        articles = generate.docx_to_articles(file_name, config=config)
        self.assertEqual(len(articles), 2)
        table_wrap_blocks = [
            block for block in articles[1].content_blocks if block.block_type == 'table-wrap']
        self.assertEqual(len(table_wrap_blocks), 4)
        self.assertTrue(table_wrap_blocks[0].content.startswith(
            '<label>Author response table 1.</label><caption><title>Expression values excluding'
            ' sex-bias FC&gt;2 (ancestry not considered).</title></caption><table frame="hsides"'
            ' rules="groups"><thead><tr><th /><th><p><italic>S. japonicum</italic></p>'
            '<p>schistosomula</p></th>'))


class TestLabels(unittest.TestCase):

    def test_labels_kitchen_sink(self):
        xml_string = read_fixture('kitchen_sink.xml')
        expected = [
            OrderedDict([
                ('id', 'sa1fig1'),
                ('type', 'fig'),
                ('text', 'Decision letter image 1.')
            ]),
            OrderedDict([
                ('id', 'sa2fig1'),
                ('type', 'fig'),
                ('text', 'Author response image 1.')
            ]),
            OrderedDict([
                ('id', 'sa2video1'),
                ('type', 'video'),
                ('text', 'Author response video 1.')
            ]),
            OrderedDict([
                ('id', 'sa2table1'),
                ('type', 'table'),
                ('text', 'Author response table 1.')
            ])
        ]
        article_xml = ElementTree.fromstring(xml_string)
        asset_labels = generate.labels(article_xml)
        self.assertEqual(asset_labels, expected)

    def test_labels_39122(self):
        file_name = data_path('Dutzler 39122 edit.docx')
        expected = [
            OrderedDict([
                ('id', 'sa2fig1'),
                ('type', 'fig'),
                ('text', 'Author response image 1.')
            ]),
            OrderedDict([
                ('id', 'sa2fig2'),
                ('type', 'fig'),
                ('text', 'Author response image 2.')
            ])
        ]
        config = parse_raw_config(raw_config('elife'))
        pretty_xml = generate.generate_xml_from_docx(
            file_name, pretty=True, indent="    ", config=config)
        article_xml = ElementTree.fromstring(pretty_xml)
        asset_labels = generate.labels(article_xml)
        self.assertEqual(asset_labels, expected)


class TestAssetXrefTags(unittest.TestCase):

    def test_asset_xref_tags(self):
        xml_string = (
            '<body>'
            '<p>First paragraph.</p>'
            '<p>An Author response video 1.</p>'
            '<media id="sa2video1"><label>Author response video 1</label></media>'
            '</body>'
        )
        expected = (
            b'<body>'
            b'<p>First paragraph.</p>'
            b'<p>An <xref ref-type="video" rid="sa2video1">Author response video 1</xref>.</p>'
            b'<media id="sa2video1"><label>Author response video 1</label></media>'
            b'</body>'
        )
        article_xml = ElementTree.fromstring(xml_string)
        generate.asset_xref_tags(article_xml)
        article_xml_string = ElementTree.tostring(article_xml)
        self.assertEqual(article_xml_string, expected)

    def test_asset_xref_tags_fig(self):
        """test fix highlight also where the paragraph is after the graphic tag"""
        xml_string = (
            '<body xmlns:xlink="http://www.w3.org/1999/xlink">'
            '<p>First paragraph.</p>'
            '<p>Another paragraph.</p>'
            '<p>An Author response image 1.</p>'
            '<fig id="sa2fig1"><label>Author response image 1.</label>'
            '<graphic mimetype="image" xlink:href="elife-00002-sa2-fig1.jpg"/>'
            '</fig>'
            '<media id="sa2video1"><label>Author response video 1</label></media>'
            '<p>2nd Author response image 1.</p>'
            '<p>Next paragraph.</p>'
            '<p>3rd Author response image 1.</p>'
            '<p>4th Author response image 1.</p>'
            '</body>'
        )
        expected = (
            b'<body xmlns:xlink="http://www.w3.org/1999/xlink">'
            b'<p>First paragraph.</p>'
            b'<p>Another paragraph.</p>'
            b'<p>An <xref ref-type="fig" rid="sa2fig1">Author response image 1</xref>.</p>'
            b'<fig id="sa2fig1"><label>Author response image 1.</label>'
            b'<graphic mimetype="image" xlink:href="elife-00002-sa2-fig1.jpg" />'
            b'</fig>'
            b'<media id="sa2video1"><label>Author response video 1</label></media>'
            b'<p>2nd <xref ref-type="fig" rid="sa2fig1">Author response image 1</xref>.</p>'
            b'<p>Next paragraph.</p>'
            b'<p>3rd <xref ref-type="fig" rid="sa2fig1">Author response image 1</xref>.</p>'
            b'<p>4th <xref ref-type="fig" rid="sa2fig1">Author response image 1</xref>.</p>'
            b'</body>'
        )
        article_xml = ElementTree.fromstring(xml_string)
        generate.asset_xref_tags(article_xml)
        article_xml_string = ElementTree.tostring(article_xml)
        self.assertEqual(article_xml_string, expected)


class TestProfileAssetLabels(unittest.TestCase):

    def test_profile_asset_labels_empty(self):
        labels = []
        expected = []
        self.assertEqual(generate.profile_asset_labels(labels), expected)

    def test_profile_asset_labels(self):
        labels = [
            'Author response image 1',
            'Author response image 1A',
            'Author response image 1A-F',
            'Author response image 1B'
        ]
        expected = [
            OrderedDict([('label', 'Author response image 1'), ('unique', False)]),
            OrderedDict([('label', 'Author response image 1A'), ('unique', False)]),
            OrderedDict([('label', 'Author response image 1A-F'), ('unique', True)]),
            OrderedDict([('label', 'Author response image 1B'), ('unique', True)]),
        ]
        self.assertEqual(generate.profile_asset_labels(labels), expected)


class TestSortLabels(unittest.TestCase):

    def test_sort_labels_empty(self):
        labels_data = []
        expected = []
        self.assertEqual(generate.sort_labels(labels_data), expected)

    def test_sort_labels(self):
        labels_data = [
            OrderedDict([('label', 'Author response image 1'), ('unique', False)]),
            OrderedDict([('label', 'Author response image 1A'), ('unique', False)]),
            OrderedDict([('label', 'Author response image 1A-F'), ('unique', True)]),
            OrderedDict([('label', 'Author response image 1B'), ('unique', True)]),
        ]
        expected = [
            OrderedDict([('label', 'Author response image 1A-F'), ('unique', True)]),
            OrderedDict([('label', 'Author response image 1B'), ('unique', True)]),
            OrderedDict([('label', 'Author response image 1'), ('unique', False)]),
            OrderedDict([('label', 'Author response image 1A'), ('unique', False)]),
        ]
        self.assertEqual(generate.sort_labels(labels_data), expected)


@ddt
class TestLabelMatches(unittest.TestCase):
    @data(
        {
            'xml_string': '',
            'xref_open_tag': '',
            'label_text': '',
            'expected_matches': [],
        },
        {
            'xml_string': 'In Author response image 1',
            'xref_open_tag': '<xref ref-type="fig" rid="sa2fig1">',
            'label_text': 'Author response image 1',
            'expected_matches': ['Author response image 1'],
        },
        {
            'xml_string': (
                'In Author response image 1 and Author response image 1B '
                'and Author response image 1B-F and Author response image 1A and B '
                ' and Author response image 1B again.'),
            'xref_open_tag': '<xref ref-type="fig" rid="sa2fig1">',
            'label_text': 'Author response image 1',
            'expected_matches': [
                'Author response image 1',
                'Author response image 1B',
                'Author response image 1B-F',
                'Author response image 1A',
                'Author response image 1B'
            ]
        },
        {
            'xml_string': (
                'In Author response image 1 and already tagged '
                '<xref ref-type="fig" rid="sa2fig1">Author response image 1B</xref>'),
            'xref_open_tag': '<xref ref-type="fig" rid="sa2fig1">',
            'label_text': 'Author response image 1',
            'expected_matches': ['Author response image 1'],
        },
    )
    def test_label_matches(self, test_data):
        matches = generate.label_matches(
            test_data.get('xml_string'),
            test_data.get('xref_open_tag'),
            test_data.get('label_text'))
        self.assertEqual(matches, test_data.get('expected_matches'))


@ddt
class TestXmlStringAssetXref(unittest.TestCase):

    @data(
        {
            'xml_string': (
                '<p>In Author response image 1, yes.</p>'
            ),
            'asset_labels': [
                OrderedDict([
                    ('id', 'sa2fig1'),
                    ('type', 'fig'),
                    ('text', 'Author response image 1')
                ])],
            'expected': (
                '<p>In <xref ref-type="fig" rid="sa2fig1">'
                'Author response image 1</xref>, yes.</p>'
            )
        },
        {
            'xml_string': (
                '<p>In the figure (Author response image 1B), a yes.</p>'
            ),
            'asset_labels': [
                OrderedDict([
                    ('id', 'sa2fig1'),
                    ('type', 'fig'),
                    ('text', 'Author response image 1')
                ])],
            'expected': (
                '<p>In the figure (<xref ref-type="fig" rid="sa2fig1">'
                'Author response image 1B</xref>), a yes.</p>'
            )
        },
        {
            'xml_string': (
                '<p>In Author response image 1A-D, also yes.</p>'
            ),
            'asset_labels': [
                OrderedDict([
                    ('id', 'sa2fig1'),
                    ('type', 'fig'),
                    ('text', 'Author response image 1')
                ])],
            'expected': (
                '<p>In <xref ref-type="fig" rid="sa2fig1">'
                'Author response image 1A-D</xref>, also yes.</p>'
            )
        },
        {
            'xml_string': (
                '<p>Potential overlapping Author response image 1A-D, '
                'and Author response image 1A.</p>'
            ),
            'asset_labels': [
                OrderedDict([
                    ('id', 'sa2fig1'),
                    ('type', 'fig'),
                    ('text', 'Author response image 1')
                ])],
            'expected': (
                '<p>Potential overlapping <xref ref-type="fig" rid="sa2fig1">'
                'Author response image 1A-D</xref>, and '
                '<xref ref-type="fig" rid="sa2fig1">Author response image 1A</xref>.</p>'
            )
        },
        {
            'xml_string': (
                '<p>Author response image 1A, then more specific '
                '<italic>Author response image 1A-D</italic>.</p>'
            ),
            'asset_labels': [
                OrderedDict([
                    ('id', 'sa2fig1'),
                    ('type', 'fig'),
                    ('text', 'Author response image 1')
                ])],
            'expected': (
                '<p><xref ref-type="fig" rid="sa2fig1">'
                'Author response image 1A</xref>, then more specific <italic>'
                '<xref ref-type="fig" rid="sa2fig1">Author response image 1A-D</xref></italic>.</p>'
            )
        },
        {
            'xml_string': (
                '<p>Author response image 1A</p>'
            ),
            'asset_labels': [
                OrderedDict([
                    ('id', 'sa2fig1'),
                    ('type', 'fig'),
                    ('text', '')
                ])],
            'expected': (
                '<p>Author response image 1A</p>'
            )
        },
    )
    def test_xml_string_asset_xref(self, test_data):
        modified_xml_string = generate.xml_string_asset_xref(
            test_data.get('xml_string'), test_data.get('asset_labels'))
        self.assertEqual(modified_xml_string, test_data.get('expected'))


class TestGenerateMaxLevel(unittest.TestCase):

    def test_generate_max_level(self):
        """test exceeding the MAX_LEVEL of nested content"""
        max_level_original = generate.MAX_LEVEL
        generate.MAX_LEVEL = 1
        # add two levels of nested content
        article = helpers.base_decision_letter()
        parent_block = ContentBlock("p", "First level paragraph.")
        child_block = ContentBlock("p", "Second level paragraph.")
        parent_block.content_blocks.append(child_block)
        article.content_blocks.append(parent_block)
        articles = [article]
        self.assertRaises(Exception, generate.generate, articles)
        # reset the module MAX_LEVEL value
        generate.MAX_LEVEL = max_level_original
