# coding=utf-8

import sys
import unittest
from collections import OrderedDict
from xml.etree import ElementTree
from elifearticle.article import Article, ContentBlock
from letterparser import build
from letterparser.generate import output_xml
from letterparser.conf import raw_config, parse_raw_config
from tests import read_fixture


class TestSplitContentSections(unittest.TestCase):
    def setUp(self):
        self.config = parse_raw_config(raw_config("elife"))

    def test_split_content_sections(self):
        sections = {
            "content": (
                '<p>One<xref xlink:href="" /></p>'
                + "<list><list-item><p>Extra</p></list-item></list><p>Two</p>"
                + "<disp-quote><p>Quotation 1</p><p>Quotation 2</p></disp-quote>"
            )
        }
        expected = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    (
                        "content",
                        (
                            '<p xmlns:xlink="http://www.w3.org/1999/xlink">'
                            + 'One<xref xlink:href="" /></p>'
                        ),
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "list"),
                    ("content", "<list><list-item><p>Extra</p></list-item></list>"),
                ]
            ),
            OrderedDict([("tag_name", "p"), ("content", "<p>Two</p>")]),
            OrderedDict([("tag_name", "p"), ("content", "<p>Quotation 1</p>")]),
            OrderedDict([("tag_name", "p"), ("content", "<p>Quotation 2</p>")]),
        ]
        result = build.split_content_sections(sections)
        self.assertEqual(result, expected)

    def test_split_content_sections_author_response_image(self):
        """parse author response image snippet of content JATS into sections"""
        section = OrderedDict(
            [
                ("section_type", "author_response"),
                ("content", read_fixture("author_response_image_1.txt")),
            ]
        )
        expected = read_fixture("author_response_image_1_sections.py")
        sections = build.split_content_sections(section)
        if sys.version_info < (3, 8):
            # pre Python 3.8 tag attributes are in a different order
            sections[-1]["content"] = sections[-1]["content"].replace(
                '<mml:math alttext="n" display="inline">',
                '<mml:math display="inline" alttext="n">',
            )
        self.assertEqual(sections, expected)


class TestCleanMath(unittest.TestCase):
    def test_clean_math_alternatives(self):
        xml_string = (
            '<root xmlns:mml="http://www.w3.org/1998/Math/MathML"><p><disp-formula>'
            + "<alternatives><tex-math><![CDATA[\\beta]]></tex-math><mml:math><mml:mi>β</mml:mi>"
            + "</mml:math></alternatives>"
            + "</disp-formula></p></root>"
        )
        section_xml = ElementTree.fromstring(xml_string)
        expected = (
            b'<?xml version="1.0" encoding="utf-8"?><root xmlns:mml="'
            + b'http://www.w3.org/1998/Math/MathML"><p><disp-formula>'
            + b'<mml:math alttext="\\beta"><mml:mi>\xce\xb2</mml:mi></mml:math>'
            + b"</disp-formula></p></root>"
        )
        clean_element = build.clean_math_alternatives(section_xml)
        xml_string = output_xml(clean_element)
        self.assertEqual(xml_string, expected)


class TestDefaultPreamble(unittest.TestCase):
    def test_default_preamble_no_config(self):
        """default preamble if no config specified"""
        self.assertIsNone(build.default_preamble(None))


class TestBuildDoi(unittest.TestCase):
    def setUp(self):
        self.config = parse_raw_config(raw_config("elife"))

    def test_build_doi(self):
        file_name = "folder/Dutzler 39122 edit.docx"
        id_value = "sa1"
        expected = "10.7554/eLife.39122.sa1"
        doi = build.build_doi(file_name, id_value, self.config)
        self.assertEqual(doi, expected)

    def test_build_doi_no_file_name(self):
        file_name = None
        id_value = "sa1"
        doi = build.build_doi(file_name, id_value, self.config)
        self.assertIsNone(doi)

    def test_build_doi_no_config(self):
        file_name = "folder/Dutzler 39122 edit.docx"
        id_value = "sa1"
        doi = build.build_doi(file_name, id_value, None)
        self.assertIsNone(doi)


class TestExtractLabelTitleContent(unittest.TestCase):
    def test_simple_title(self):
        content = "<bold>Label</bold>Title. Caption.&lt;/Legend&gt;"
        label, title, caption = build.extract_label_title_content(content)
        self.assertEqual(label, "Label")
        self.assertEqual(title, "Title.")
        self.assertEqual(caption, "Caption.")

    def test_organism_title(self):
        content = (
            "<bold>Label</bold>In <italic>B. subtilis</italic>, the title."
            " Caption.&lt;/Legend&gt;"
        )
        label, title, caption = build.extract_label_title_content(content)
        self.assertEqual(label, "Label")
        self.assertEqual(title, "In <italic>B. subtilis</italic>, the title.")
        self.assertEqual(caption, "Caption.")

    def test_two_bold_tags(self):
        "edge case with more than one bold tag and second one is around the title full stop"
        content = (
            "<bold>Label</bold>The title<bold>.</bold> Another <bold>bold term</bold>."
            "Another paragraph.&lt;/Legend&gt;"
        )
        label, title, caption = build.extract_label_title_content(content)
        self.assertEqual(label, "Label")
        self.assertEqual(
            title, "The title<bold>.</bold> Another <bold>bold term</bold>."
        )
        self.assertEqual(caption, "Another paragraph.")

    def test_ext_link_tag(self):
        "edge case with an ext-link tag in the title and challenging full stop separations"
        content = '&lt;Author response image 2&gt;&lt;Author response image 2 title/legend&gt;<bold>Author response image 2.</bold> (Figure 2A from <ext-link ext-link-type="uri" xlink:href="https://example.org/one/two">(Anonymous et al., 2011)</ext-link>)<bold>.</bold> Comparison of Tests against Γ ( 4,5) (a = 0.05). The normality tests used were severely underpowered for n&lt;100.&lt;/Author response image 2 title/legend&gt;'
        label, title, caption = build.extract_label_title_content(content)
        self.assertEqual(label, "Author response image 2.")
        self.assertEqual(
            title,
            '(Figure 2A from <ext-link ext-link-type="uri" xlink:href="https://example.org/one/two">(Anonymous et al., 2011)</ext-link>)<bold>.</bold> Comparison of Tests against Γ ( 4,5) (a = 0.',
        )
        self.assertEqual(
            caption,
            "05). The normality tests used were severely underpowered for n&lt;100.",
        )

    def test_mml_tag(self):
        "edge case where a full stop in math formula should not be used as separate parts"
        content = '&lt;Author response image 1&gt;&lt;Author response image 1 title/legend&gt;<bold>Author response image 1.</bold> For one participant <inline-formula><mml:math alttext="" display="inline"><mml:mspace width="0.222em" /></mml:math></inline-formula> is a formula.&lt;/Author response image 1 title/legend&gt;'
        label, title, caption = build.extract_label_title_content(content)
        self.assertEqual(label, "Author response image 1.")
        self.assertEqual(
            title,
            'For one participant <inline-formula><mml:math alttext="" display="inline"><mml:mspace width="0.222em" /></mml:math></inline-formula> is a formula.',
        )
        self.assertEqual(
            caption,
            None,
        )


class TestBuildFig(unittest.TestCase):
    def test_build_fig(self):
        content = read_fixture("author_response_fig_content.txt")
        expected = read_fixture("author_response_fig_content.py")
        fig_content = build.build_fig(content)
        self.assertEqual(fig_content, expected)

    def test_build_fig_simple_title(self):
        """example of a title with no full stop"""
        content = (
            "&lt;Author response image 1 title/legend&gt;"
            "<bold>Label</bold>Title"
            "&lt;/Author response image 1 title/legend&gt;"
        )
        expected = OrderedDict(
            [("label", "Label"), ("title", "Title"), ("content", None)]
        )
        fig_content = build.build_fig(content)
        self.assertEqual(fig_content, expected)


class TestBuildVideo(unittest.TestCase):
    def test_build_fig(self):
        content = read_fixture("author_response_video_content.txt")
        expected = read_fixture("author_response_video_content.py")
        # for now reusing build_fig function which satisifes the same situation
        video_content = build.build_fig(content)
        self.assertEqual(video_content, expected)


class TestBuildDispQuote(unittest.TestCase):
    def test_disp_quote_element(self):
        content = "<p>One.</p><p>Two.</p>"
        expected = b"<disp-quote><p>One.</p><p>Two.</p></disp-quote>"
        tag_content = build.disp_quote_element(content)
        tag_xml = ElementTree.tostring(tag_content)
        self.assertEqual(tag_xml, expected)


class TestBuildTableWrap(unittest.TestCase):
    def test_build_table(self):
        """example of a title"""
        content = (
            "<bold>Author response Table 1.</bold>"
            "&lt;Author response table 1 title/legend&gt;"
            "Author response table"
            "&lt;/Author response table 1 title/legend&gt;"
            "<table></table>"
        )
        expected = OrderedDict(
            [
                ("table", "<table></table>"),
                ("label", "Author response Table 1."),
                ("title", "Author response table"),
                ("content", None),
            ]
        )
        table_content = build.build_table_wrap(content)
        self.assertEqual(table_content, expected)


class TestBuildTableWrapElement(unittest.TestCase):
    def test_table_wrap_element(self):
        label = "Author response Table 1."
        title = "Author response table"
        content = "Optional caption."
        table = "<table></table>"
        expected = (
            b"<table-wrap><label>Author response Table 1.</label>"
            b"<caption><title>Author response table</title>"
            b"<p>Optional caption.</p></caption>"
            b'<table frame="hsides" rules="groups" /></table-wrap>'
        )
        tag_content = build.table_wrap_element(label, title, content, table)
        tag_xml = ElementTree.tostring(tag_content)
        self.assertEqual(tag_xml, expected)


class TestBuildSubArticle(unittest.TestCase):
    def setUp(self):
        self.config = parse_raw_config(raw_config("elife"))

    def test_build_sub_article_video(self):
        doi = "10.7554/eLife.00666"
        id_value = "sa2"
        article_type = "reply"
        manuscript = 666
        content = read_fixture("author_response_video_1.txt")
        section = OrderedDict(
            [("section_type", "author_response"), ("content", content)]
        )
        expected_content = (
            "<label>Author response video 1.</label><caption><title>Title up to first full stop."
            "</title><p>Caption <sup>2+</sup>.</p></caption>"
        )
        article = build.build_sub_article(
            section, self.config, article_type, id_value, doi, manuscript
        )
        self.assertEqual(article.doi, doi)
        self.assertEqual(article.id, id_value)
        self.assertEqual(article.manuscript, manuscript)
        self.assertEqual(article.article_type, article_type)
        self.assertEqual(article.content_blocks[0].block_type, "media")
        self.assertEqual(
            article.content_blocks[0].attr["xlink:href"], "elife-00666-sa2-video1"
        )
        self.assertEqual(article.content_blocks[0].content, expected_content)

    def test_build_sub_article_graphic_ext_link(self):
        doi = "10.7554/eLife.00666"
        id_value = "sa2"
        article_type = "reply"
        manuscript = 666
        content = (
            "<p>&lt;Author response image 1&gt;</p><p>&lt;Author response image 1 title/legend&gt;"
            "<bold>Author response image 1.</bold>"
            ' Title with <ext-link xlink:href="https://example.org/">link</ext-link>.'
            " Caption <sup>2+</sup>.&lt;/Author response image 1 title/legend&gt;</p>"
        )
        section = OrderedDict(
            [("section_type", "author_response"), ("content", content)]
        )
        expected_content = (
            "<label>Author response image 1.</label>"
            "<caption>"
            '<title>Title with <ext-link xlink:href="https://example.org/">link</ext-link>.</title>'
            "<p>Caption <sup>2+</sup>.</p></caption>"
            '<graphic mimetype="image" xlink:href="elife-00666-sa2-fig1" />'
        )
        article = build.build_sub_article(
            section, self.config, article_type, id_value, doi, manuscript
        )
        self.assertEqual(article.doi, doi)
        self.assertEqual(article.id, id_value)
        self.assertEqual(article.manuscript, manuscript)
        self.assertEqual(article.article_type, article_type)
        self.assertEqual(article.content_blocks[0].block_type, "fig")
        self.assertEqual(article.content_blocks[0].content, expected_content)


class TestSetContentBlocks(unittest.TestCase):
    def test_author_response_image(self):
        content = read_fixture("author_response_image_1.txt")
        section = OrderedDict(
            [("section_type", "author_response"), ("content", content)]
        )
        expected = read_fixture("author_response_image_1_content_block.py")
        if sys.version_info < (3, 8):
            # pre Python 3.8 tag attributes are automatically alphabetised
            expected.content = expected.content.replace(
                '<mml:math display="inline" alttext="n">',
                '<mml:math alttext="n" display="inline">',
            )
        article = Article()
        build.set_content_blocks(article, section)
        self.assertEqual(article.content_blocks[0].block_type, expected.block_type)
        self.assertEqual(article.content_blocks[0].content, expected.content)

    def test_author_response_video(self):
        content = read_fixture("author_response_video_1.txt")
        section = OrderedDict(
            [("section_type", "author_response"), ("content", content)]
        )
        expected = read_fixture("author_response_video_1_content_block.py")
        article = Article()
        build.set_content_blocks(article, section)
        self.assertEqual(article.content_blocks[0].block_type, expected.block_type)
        self.assertEqual(article.content_blocks[0].attr, expected.attr)
        self.assertEqual(article.content_blocks[0].content, expected.content)

    def test_decision_letter_italic_disp_quote(self):
        """non-author_response will not have italic paragraphs converted to disp-quote"""
        content = "<italic>Italic paragraph.</italic>"
        section_content = "<p>%s</p>" % content
        section = OrderedDict(
            [("section_type", "decision_letter"), ("content", section_content)]
        )
        expected = ContentBlock("p", content)
        article = Article()
        build.set_content_blocks(article, section)
        self.assertEqual(article.content_blocks[0].block_type, expected.block_type)
        self.assertEqual(article.content_blocks[0].content, expected.content)

    def test_author_response_italic_disp_quote(self):
        """author_response will get italic paragraphs converted to disp-quote"""
        content = "Italic paragraph."
        section_content = "<p><italic>%s</italic></p>" % content
        expected_content = "<p>%s</p>" % content
        section = OrderedDict(
            [("section_type", "author_response"), ("content", section_content)]
        )
        expected = ContentBlock(
            "disp-quote", expected_content, {"content-type": "editor-comment"}
        )
        article = Article()
        build.set_content_blocks(article, section)
        self.assertEqual(article.content_blocks[0].block_type, expected.block_type)
        self.assertEqual(article.content_blocks[0].attr, expected.attr)
        self.assertEqual(article.content_blocks[0].content, expected.content)


class TestProcessP(unittest.TestCase):
    def test_p_basic(self):
        content = "<p>Basic.</p>"
        prev = {}
        expected = ("Basic.", "p", None, "append", None)
        self.assertEqual(build.process_p_content(content, prev), expected)

    def test_p_add_previous(self):
        content = "<p>Basic.</p>"
        prev = {"content": "Previous."}
        expected = ("Basic.", "p", None, "add", None)
        self.assertEqual(build.process_p_content(content, prev), expected)

    def test_p_append_disp_formula(self):
        content = "<p><disp-formula></disp-formula></p>"
        prev = {"content": "<disp-formula></disp-formula>"}
        expected = ("<disp-formula></disp-formula>", "p", None, "append", None)
        self.assertEqual(build.process_p_content(content, prev), expected)

    def test_process_p_author_image_start(self):
        content = "&lt;Author response image 1&gt;"
        prev = {}
        expected = ("&lt;Author response image 1&gt;", "p", None, "add", "fig")
        self.assertEqual(build.process_p_content(content, prev), expected)

    def test_process_p_author_image_end(self):
        content = "blah blah&lt;/Author response image 1 title/legend&gt;"
        prev = {"wrap": "fig"}
        expected = (
            "blah blah&lt;/Author response image 1 title/legend&gt;",
            "p",
            None,
            "add",
            None,
        )
        self.assertEqual(build.process_p_content(content, prev), expected)

    def test_process_p_decision_image_start(self):
        content = "&lt;Decision letter image 2&gt;"
        prev = {}
        expected = ("&lt;Decision letter image 2&gt;", "p", None, "add", "fig")
        self.assertEqual(build.process_p_content(content, prev), expected)

    def test_process_p_decision_image_end(self):
        content = "blah blah&lt;/Decision letter image 2 title/legend&gt;"
        prev = {"wrap": "fig"}
        expected = (
            "blah blah&lt;/Decision letter image 2 title/legend&gt;",
            "p",
            None,
            "add",
            None,
        )
        self.assertEqual(build.process_p_content(content, prev), expected)

    def test_process_p_author_video_start(self):
        content = "&lt;Author response video 1&gt;"
        prev = {}
        expected = ("&lt;Author response video 1&gt;", "p", None, "add", "media")
        self.assertEqual(build.process_p_content(content, prev), expected)

    def test_process_p_author_video_end(self):
        content = "blah blah&lt;/Author response video 1 title/legend&gt;"
        prev = {"wrap": "fig"}
        expected = (
            "blah blah&lt;/Author response video 1 title/legend&gt;",
            "p",
            None,
            "add",
            None,
        )
        self.assertEqual(build.process_p_content(content, prev), expected)

    def test_process_p_italic_inline_formula(self):
        content = (
            "<p><italic>2. The description ...</italic>"
            "<inline-formula><alternatives>"
            "<tex-math><![CDATA[- 2\\widetilde{v}]]></tex-math>"
            '<mml:math display="inline" xmlns:mml="http://www.w3.org/1998/Math/MathML">'
            "<mml:mrow><mml:mo>−</mml:mo><mml:mn>2</mml:mn><mml:mover><mml:mi>v</mml:mi>"
            '<mml:mo accent="true">∼</mml:mo></mml:mover></mml:mrow></mml:math>'
            "</alternatives></inline-formula><italic>.</italic></p>"
        )
        prev = {}
        prefs = {"italic_to_disp_quote": True}
        expected = (
            (
                "<p>2. The description ..."
                "<inline-formula><alternatives>"
                "<tex-math><![CDATA[- 2\\widetilde{v}]]></tex-math>"
                '<mml:math display="inline" xmlns:mml="http://www.w3.org/1998/Math/MathML">'
                "<mml:mrow><mml:mo>−</mml:mo><mml:mn>2</mml:mn><mml:mover><mml:mi>v</mml:mi>"
                '<mml:mo accent="true">∼</mml:mo></mml:mover></mml:mrow></mml:math>'
                "</alternatives></inline-formula>.</p>"
            ),
            "p",
            None,
            "add",
            "disp-quote",
        )
        self.assertEqual(build.process_p_content(content, prev, prefs), expected)
