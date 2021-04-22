# coding=utf-8

import unittest
from ddt import ddt, data
from letterparser import utils
from tests import data_path, read_fixture


@ddt
class TestRemoveNonBreakingSpace(unittest.TestCase):

    @data(
        {
            "comment": "None value",
            "string": None,
            "expected": ""
        },
        {
            "comment": "Basic string",
            "string": "string",
            "expected": "string"
        },
        {
            "comment": "Test '\\xc2\\xa0' character",
            "string": "\xc2\xa0",
            "expected": ""
        },
        {
            "comment": "Test '\\xa0' character",
            "string": "\xa0",
            "expected": ""
        },
        {
            "comment": "Test '\\xc2\\xa0\\xa0' sequence",
            "string": "\xc2\xa0\xa0",
            "expected": ""
        },
        )
    def test_remove_non_breaking_space(self, test_data):
        new_string = utils.remove_non_breaking_space(test_data.get("string"))
        self.assertEqual(
            new_string, test_data.get("expected"),
            "{value} does not equal {expected}, scenario {comment}".format(
                value=new_string,
                expected=test_data.get("expected"),
                comment=test_data.get("comment")))


@ddt
class TestRemoveStrike(unittest.TestCase):

    @data(
        {
            "comment": "None value",
            "string": None,
            "expected": ""
        },
        {
            "comment": "Basic string",
            "string": "string",
            "expected": "string"
        },
        {
            "comment": "One strike tag",
            "string": "This is <strike>not</strike> that.",
            "expected": "This is that."
        },
        {
            "comment": "Two strike tags",
            "string": "This is <strike>really</strike> <strike>not</strike> that.",
            "expected": "This is that."
        },
        {
            "comment": "Strike tag around italic",
            "string": "This is <strike><italic>really</italic></strike> that.",
            "expected": "This is that."
        },
        {
            "comment": "Strike tag at end of sentence",
            "string": "This is really <strike>the end</strike>.",
            "expected": "This is really."
        },
        {
            "comment": "Strike tag at end of sentence",
            "string": "<strike>Hmm...</strike> Just testing.",
            "expected": "Just testing."
        },
        )
    def test_remove_strike(self, test_data):
        new_string = utils.remove_strike(test_data.get("string"))
        self.assertEqual(
            new_string, test_data.get("expected"),
            "{value} does not equal {expected}, scenario {comment}".format(
                value=new_string,
                expected=test_data.get("expected"),
                comment=test_data.get("comment")))


@ddt
class TestNewLineReplaceWith(unittest.TestCase):

    @data(
        {
            "comment": "None values",
            "line_one": None,
            "line_two": None,
            "expected": ""
        },
        {
            "comment": "strings only",
            "line_one": "one",
            "line_two": "two",
            "expected": "<break /><break />"
        },
        {
            "comment": "string and tag",
            "line_one": "higher precision than",
            "line_two": "<italic>σ<sub>h</sub></italic>.",
            "expected": "<break /><break />"
        },
        {
            "comment": "both have tags",
            "line_one": "<alternatives>",
            "line_two": "<tex-math><![CDATA[n]]></tex-math>",
            "expected": ""
        },
        {
            "comment": "italic paragraph with a trailing space",
            "line_one": "<p><italic> ",
            "line_two": "1) I am not sure...",
            "expected": ""
        },
        {
            "comment": "continued italic paragraph",
            "line_one": "... rectification observed. ",
            "line_two": "</italic></p>",
            "expected": ""
        },
        {
            "comment": "paragraph break",
            "line_one": "</italic></p>",
            "line_two": "<p>In our analysis...",
            "expected": ""
        },
        {
            "comment": "continued italic tag",
            "line_one": "detailed below. ",
            "line_two": "<italic>Reviewer #1: ",
            "expected": "<break /><break />"
        },
        {
            "comment": "split italic tag",
            "line_one": "<italic>Reviewer #1: ",
            "line_two": "</italic>",
            "expected": ""
        },
        {
            "comment": "finished paragraph",
            "line_one": "revised submission. ",
            "line_two": "Summary:</p>",
            "expected": "<break /><break />"
        },
        {
            "comment": "italic paragraph",
            "line_one": "<p><italic>Reviewer #1:",
            "line_two": "In this manuscript, ....",
            "expected": "<break /><break />"
        },
        )
    def test_new_line_replace_with(self, test_data):
        replace_with = utils.new_line_replace_with(
            test_data.get("line_one"), test_data.get("line_two"))
        self.assertEqual(
            replace_with, test_data.get("expected"),
            "{value} does not equal {expected}, scenario {comment}".format(
                value=replace_with,
                expected=test_data.get("expected"),
                comment=test_data.get("comment")))


@ddt
class TestCollapseNewlines(unittest.TestCase):

    @data(
        {
            "comment": "None value",
            "string": None,
            "expected": None
        },
        {
            "comment": "No tags around new line character",
            "string": "K<sub>M</sub> of chloride\nconduction between 300-400 mM",
            "expected": "K<sub>M</sub> of chloride<break /><break />conduction between 300-400 mM"
        },
        {
            "comment": "Tags before and after new line character",
            "string": "were calculated using</p>\n<p><disp-formula><alternatives>\n<tex-math>",
            "expected": "were calculated using</p><p><disp-formula><alternatives><tex-math>"
        },
        {
            "comment": "New line after Author response section",
            "string": (
                "<p><bold>Author response</bold><italic>\nEssential revisions: ...</italic></p>"),
            "expected": (
                "<p><bold>Author response</bold><break /><break />"
                "<italic>Essential revisions: ...</italic></p>")
        },
        {
            "comment": "New line after italic tag and before italic close tag",
            "string": "<p>One<italic>\nTwo\n</italic></p>",
            "expected": "<p>One<break /><break /><italic>Two</italic></p>"
        },
        {
            "comment": "Italic paragraph with new line at beginning",
            "string": "<p><italic> \nParagraph \n</italic></p>",
            "expected": "<p><italic> Paragraph </italic></p>"
        },
        {
            "comment": "New line prior to bold section heading",
            "string": "<p>Previous paragraph\n<bold>Author response</bold></p>",
            "expected": "<p>Previous paragraph<break /><break /><bold>Author response</bold></p>"
        },
        {
            "comment": "Italic close tag on its own line",
            "string": (
                "<p><italic>\nReviewer #2:\nThe manuscript ....\n</italic>\nTo minimize ....."
                "</p>\n<p><italic>"),
            "expected": (
                "<p><italic>Reviewer #2:<break /><break />The manuscript ...."
                "</italic><break /><break />To minimize .....</p><p><italic>")
        },
        {
            "comment": "Italic open tag on its own line",
            "string": "<p>Paragraph\n<italic>\nItalic content</italic></p>",
            "expected": (
                "<p>Paragraph<break /><break /><italic>"
                "Italic content</italic></p>")
        },
        {
            "comment": "Simple italic new line",
            "string": "Previous.\n<italic>Reviewer #1:\n</italic>Next paragraph\n",
            "expected": "Previous.<break /><break /><italic>Reviewer #1:</italic>Next paragraph"
        },
        {
            "comment": "Italic paragraph with new line inside",
            "string": (
                "<p><italic>We have <italic>provided</italic> ....\n"
                "10) Figure 1: The authors assume ....\n</italic></p>"),
            "expected": (
                "<p><italic>We have <italic>provided</italic> ....<break /><break />"
                "10) Figure 1: The authors assume ....</italic></p>")
        },
        {
            "comment": "Another example of new line inside italic paragraph",
            "string": "<p>We have provided ....\n<italic>10) Figure 1: ....\n</italic></p>",
            "expected": (
                "<p>We have provided ....<break /><break /><italic>"
                "10) Figure 1: ....</italic></p>")
        },
        {
            "comment": "More complicated example",
            "string": (
                "\nTo minimize ....</p>\n<p><italic>\n- Subsection ....\n</italic>\n"
                "We have modified ....</p>\n"),
            "expected": (
                "<break /><break />To minimize ....</p><p>"
                "<italic>- Subsection ....</italic><break /><break />"
                "We have modified ....</p><break /><break />")
        },
        {
            "comment": "disp-quote example",
            "string": (
                "\n<disp-quote>\n  <p>Normal.</p>\n  "
                "<p><italic>\nItalic.\n  </italic></p>\n  "
                "<p>Normal again.</p>\n</disp-quote>"),
            "expected": (
                "<break /><break /><disp-quote><p>Normal.</p>"
                "<p><italic>Italic.</italic></p><p>Normal again.</p></disp-quote>")
        },
        {
            "comment": "italic close tag after a new line",
            "string": (
                "<p><italic>- How are the levels ....</p>\n"
                "</italic>We include eosinophil numbers ....</p>\n"
                "<p><italic>\n"
                "I agree ....\n"
                "</italic>We discuss our <italic>in vivo</italic> results ....</p>"),
            "expected": (
                "<p><italic>- How are the levels ....</p>"
                "</italic><break /><break />We include eosinophil numbers ....</p>"
                "<p><italic>I agree ....</italic><break /><break />"
                "We discuss our <italic>in vivo</italic> results ....</p>")
        },
        {
            "comment": "editors note italic example",
            "string": (
                "<p><italic>\n"
                "</italic>[Editors' note: ....]\n"
                "<italic>The essential point of discussion ....\n"
                "</italic></p>"),
            "expected": (
                "<p><break /><break />[Editors' note: ....]"
                "<break /><break /><italic>The essential point of discussion ....</italic></p>")
        },
        {
            "comment": "italic bullet points example",
            "string": (
                "<p><italic>\n"
                "- How are the numbers ....</italic></p>\n"
                "<p><italic>- How are the levels ...?\n"
                "</italic>We include eosinophil numbers ....</p>"),
            "expected": (
                "<p><italic>- How are the numbers ....</italic></p>"
                "<p><italic>- How are the levels ...?</italic><break /><break />"
                "We include eosinophil numbers ....</p>")
        },
        {
            "comment": "line two close italic p from 39122 example",
            "string": (
                "<p><italic>And why is σ<sub>h</sub> not shown beyond Figure 1?\n"
                "</italic></p>\n"
                "<p>We have selected ...</p>"),
            "expected": (
                "<p><italic>And why is σ<sub>h</sub> not shown beyond Figure 1?</italic></p>"
                "<p>We have selected ...</p>")
        },
        {
            "comment": "new line before an Author response bold section",
            "string": (
                "<p>Paragraph.\n"
                "Notation.\n"
                "<bold>Author response</bold></p>\n"
                "<p><italic>Reviewer #1:\n"
                "My comments are the following:\n"
                "...\n"
                "</italic></p>"),
            "expected": (
                "<p>Paragraph.<break /><break />"
                "Notation.<break /><break />"
                "<bold>Author response</bold></p>"
                "<p><italic>Reviewer #1:<break /><break />"
                "My comments are the following:<break /><break />"
                "...</italic></p>")
        },
        {
            "comment": "exact match of italic tag on one line",
            "string": (
                "<p>The sign ...\n"
                "<inline-formula><alternatives>\n"
                "<tex-math><![CDATA[{\\widetilde{v}}_{i}]]></tex-math>\n"
                '<mml:math display="inline" xmlns:mml="http://www.w3.org/1998/Math/MathML">'
                "<mml:msub><mml:mover><mml:mi>v</mml:mi>"
                '<mml:mo accent="true">∼</mml:mo>'
                "</mml:mover><mml:mi>i</mml:mi></mml:msub>"
                "</mml:math></alternatives></inline-formula> ....\n"
                "<italic>\n"
                "2. The description ...</italic>\n"
                "<inline-formula><alternatives>\n"
                "<tex-math><![CDATA[- 2\\widetilde{v}]]></tex-math>\n"
                '<mml:math display="inline" xmlns:mml="http://www.w3.org/1998/Math/MathML">'
                "<mml:mrow><mml:mo>−</mml:mo><mml:mn>2</mml:mn><mml:mover><mml:mi>v</mml:mi>"
                '<mml:mo accent="true">∼</mml:mo></mml:mover></mml:mrow>'
                "</mml:math></alternatives></inline-formula><italic>.</italic></p>"
            ),
            "expected": (
                "<p>The sign ..."
                "<inline-formula><alternatives>"
                "<tex-math><![CDATA[{\\widetilde{v}}_{i}]]></tex-math>"
                '<mml:math display="inline" xmlns:mml="http://www.w3.org/1998/Math/MathML">'
                "<mml:msub><mml:mover><mml:mi>v</mml:mi>"
                '<mml:mo accent="true">∼</mml:mo>'
                "</mml:mover><mml:mi>i</mml:mi></mml:msub>"
                "</mml:math></alternatives></inline-formula> ...."
                "<break /><break />"
                "<italic>2. The description ...</italic>"
                "<inline-formula><alternatives>"
                "<tex-math><![CDATA[- 2\\widetilde{v}]]></tex-math>"
                '<mml:math display="inline" xmlns:mml="http://www.w3.org/1998/Math/MathML">'
                "<mml:mrow><mml:mo>−</mml:mo><mml:mn>2</mml:mn><mml:mover><mml:mi>v</mml:mi>"
                '<mml:mo accent="true">∼</mml:mo></mml:mover></mml:mrow>'
                "</mml:math></alternatives></inline-formula><italic>.</italic></p>"
            ),
        },
        )
    def test_collapse_newlines(self, test_data):
        new_string = utils.collapse_newlines(test_data.get("string"))
        self.assertEqual(
            new_string, test_data.get("expected"),
            "{value} does not equal {expected}, scenario {comment}".format(
                value=new_string,
                expected=test_data.get("expected"),
                comment=test_data.get("comment")))


@ddt
class TestCleanPortion(unittest.TestCase):

    @data(
        {
            "comment": "None value",
            "root_tag": "root",
            "string": None,
            "expected": ""
        },
        {
            "comment": "Plain string",
            "root_tag": "root",
            "string": "",
            "expected": ""
        },
        {
            "comment": "root tag at start of string",
            "root_tag": "root",
            "string": "<root><p>Text</p>",
            "expected": "<p>Text</p>"
        },
        {
            "comment": "root tag at end of string",
            "root_tag": "root",
            "string": "<p>Text</p></root>",
            "expected": "<p>Text</p>"
        }
        )
    def test_collapse_newlines(self, test_data):
        new_string = utils.clean_portion(test_data.get("string"), test_data.get("root_tag"))
        self.assertEqual(
            new_string, test_data.get("expected"),
            "{value} does not equal {expected}, scenario {comment}".format(
                value=new_string,
                expected=test_data.get("expected"),
                comment=test_data.get("comment")))


class TestFileNameFunctions(unittest.TestCase):

    def setUp(self):
        self.file_name = 'folder/file.txt'

    def test_get_file_name_path(self):
        expected = 'folder'
        self.assertEqual(utils.get_file_name_path(self.file_name), expected)

    def test_get_file_name_file(self):
        expected = 'file.txt'
        self.assertEqual(utils.get_file_name_file(self.file_name), expected)


@ddt
class TestManuscriptFromFileName(unittest.TestCase):

    @data(
        {
            "file_name": None,
            "expected": None
        },
        {
            "file_name": "Dutzler 39122 edit.docx",
            "expected": "39122"
        },
        {
            "file_name": "folder/Dutzler 39122 edit.docx",
            "expected": "39122"
        },
        {
            "file_name": "folder/elife-00666.docx",
            "expected": "666"
        },
        {
            "file_name": "folder/elife-NaN.docx",
            "expected": None
        },
        )
    def test_manuscript_from_file_name(self, test_data):
        manuscript = utils.manuscript_from_file_name(test_data.get("file_name"))
        self.assertEqual(manuscript, test_data.get("expected"))


class TestOpenTag(unittest.TestCase):

    def test_open_tag(self):
        tag_name = 'italic'
        expected = '<italic>'
        self.assertEqual(utils.open_tag(tag_name), expected)

    def test_open_tag_with_attr(self):
        tag_name = 'xref'
        attr = {'id': 'sa2fig1', 'ref-type': 'fig'}
        expected = '<xref id="sa2fig1" ref-type="fig">'
        self.assertEqual(utils.open_tag(tag_name, attr), expected)


class TestRemoveComplexScriptsStyles(unittest.TestCase):

    def test_remove_complex_scripts_styles(self):
        with open(data_path('complex_scripts_document.xml'), 'rb') as open_file:
            xml_string = open_file.read()
        expected = read_fixture('complex_scripts_document_expected.xml', mode='rb')
        xml_string = utils.remove_complex_scripts_styles(xml_string)
        self.assertEqual(xml_string, expected)

    def test_remove_complex_scripts_style_edge_cases(self):
        xml_string = (
            b'<w:pPr><w:r><w:rFonts w:cs="Calibri" w:ascii="Cambria" w:hAnsi="Cambria"'
            b' w:asciiTheme="minorHAnsi" w:hAnsiTheme="minorHAnsi"/>'
            b'<w:iCs/><w:bCs><w:iCs w:val="false"/></w:r></w:pPr>'
        )
        expected = (
            b'<w:pPr><w:r><w:rFonts w:cs="Calibri" w:ascii="Cambria" w:hAnsi="Cambria"'
            b' w:asciiTheme="minorHAnsi" w:hAnsiTheme="minorHAnsi"/>'
            b'</w:r></w:pPr>'
        )
        xml_string = utils.remove_complex_scripts_styles(xml_string)
        self.assertEqual(xml_string, expected)

    def test_remove_complex_scripts_style_do_not_remove(self):
        xml_string = (
            b'<w:pPr><w:r id="a"><w:rFonts w:eastAsia="Times New Roman" w:cstheme="minorHAnsi"/>'
            b'<w:iCs/><w:bCs><w:iCs w:val="false"/></w:r></w:pPr>'
        )
        expected = xml_string
        xml_string = utils.remove_complex_scripts_styles(xml_string)
        self.assertEqual(xml_string, expected)


class TestReplaceCharacterEntities(unittest.TestCase):

    def test_replace_character_entities(self):
        xml_string = b'&quot;Test&quot; &amp; &lt;&gt;'
        expected = b'&#x0022;Test&#x0022; &#x0026; &#x003C;&#x003E;'
        xml_string = utils.replace_character_entities(xml_string)
        self.assertEqual(xml_string, expected)

    def test_replace_character_entities_string(self):
        xml_string = '&quot;Test&quot; &amp; &lt;&gt;'
        expected = b'&#x0022;Test&#x0022; &#x0026; &#x003C;&#x003E;'
        xml_string = utils.replace_character_entities(xml_string)
        self.assertEqual(xml_string, expected)


class TestFixNamespaces(unittest.TestCase):

    def setUp(self):
        self.root_tag = 'root'

    def test_fix_namespaces_blank(self):
        xml_string = b''
        expected = b''
        self.assertEqual(utils.xml_string_fix_namespaces(xml_string, self.root_tag), expected)

    def test_fix_namespaces_two_mml(self):
        xml_string = (
            b'<root xmlns:mml="http://www.w3.org/1998/Math/MathML"'
            b' xmlns:ali="http://www.niso.org/schemas/ali/1.0/"'
            b' xmlns:mml="http://www.w3.org/1998/Math/MathML"'
            b' xmlns:xlink="http://www.w3.org/1999/xlink">')
        expected = (
            b'<root xmlns:ali="http://www.niso.org/schemas/ali/1.0/"'
            b' xmlns:mml="http://www.w3.org/1998/Math/MathML"'
            b' xmlns:xlink="http://www.w3.org/1999/xlink">')
        self.assertEqual(utils.xml_string_fix_namespaces(xml_string, self.root_tag), expected)

    def test_fix_namespaces_two_xlink(self):
        xml_string = (
            b'<root xmlns:xlink="http://www.w3.org/1999/xlink"'
            b' xmlns:ali="http://www.niso.org/schemas/ali/1.0/"'
            b' xmlns:mml="http://www.w3.org/1998/Math/MathML"'
            b' xmlns:xlink="http://www.w3.org/1999/xlink">')
        expected = (
            b'<root xmlns:ali="http://www.niso.org/schemas/ali/1.0/"'
            b' xmlns:mml="http://www.w3.org/1998/Math/MathML"'
            b' xmlns:xlink="http://www.w3.org/1999/xlink">')
        self.assertEqual(utils.xml_string_fix_namespaces(xml_string, self.root_tag), expected)
