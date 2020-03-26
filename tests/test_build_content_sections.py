# coding=utf-8

import unittest
from collections import OrderedDict
from letterparser import build


class TestProcessContentSections(unittest.TestCase):

    def setUp(self):
        # prefs for author_response sections
        self.prefs = OrderedDict()
        self.prefs['italic_to_disp_quote'] = True

    def test_process_content_sections(self):
        content_sections = [
            OrderedDict([
                ("tag_name", "p"),
                ("content", 'Hello!'),
            ])
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "p")
        self.assertEqual(result[0].content, "Hello!")

    def test_process_content_sections_namespace(self):
        content_sections = [
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p xmlns:xlink="http://www.w3.org/1999/xlink">Hello!</p>'),
            ])
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "p")
        self.assertEqual(result[0].content, "Hello!")

    def test_process_content_sections_table(self):
        content_sections = [
            OrderedDict([
                ("tag_name", "table"),
                ("content", '<table></table>'),
            ])
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "table")
        self.assertEqual(result[0].content, '<table></table>')

    def test_process_content_sections_table_with_caption(self):
        content_sections = [
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<italic>Italic paragraph.</italic>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<italic>Previous paragraph.</italic>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<bold>Author response Table 1.</bold>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", (
                    '&lt;Author response table 1 title/legend&gt;Author response table'
                    '&lt;/Author response table 1 title/legend&gt;')),
            ]),
            OrderedDict([
                ("tag_name", "table"),
                ("content", '<table xmlns:mml="http://www.w3.org/1998/Math/MathML"></table>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<italic>Next paragraph.</italic>'),
            ]),
        ]
        result = build.process_content_sections(content_sections, self.prefs)
        self.assertEqual(result[0].block_type, "disp-quote")
        self.assertEqual(result[0].content, '<p>Italic paragraph.</p><p>Previous paragraph.</p>')
        self.assertEqual(result[1].block_type, "table-wrap")
        self.assertEqual(result[1].content, (
            '<label>Author response Table 1.</label>'
            '<caption><title>Author response table</title></caption>'
            '<table frame="hsides" rules="groups" />'))
        self.assertEqual(result[2].block_type, "disp-quote")
        self.assertEqual(result[2].content, '<p>Next paragraph.</p>')

    def test_process_content_sections_table_disp_quote(self):
        """test for previous block is a disp-quote type"""
        content_sections = [
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<italic>Paragraph.</italic>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<bold>Author response Table 1.</bold>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", (
                    '&lt;Author response table 1 title/legend&gt;Author response table'
                    '&lt;/Author response table 1 title/legend&gt;')),
            ]),
            OrderedDict([
                ("tag_name", "table"),
                ("content", '<table xmlns:mml="http://www.w3.org/1998/Math/MathML"></table>'),
            ])
        ]
        result = build.process_content_sections(content_sections, self.prefs)
        self.assertEqual(result[0].block_type, "disp-quote")
        self.assertEqual(result[1].block_type, "table-wrap")
        self.assertEqual(result[1].content, (
            '<label>Author response Table 1.</label>'
            '<caption><title>Author response table</title></caption>'
            '<table frame="hsides" rules="groups" />'))

    def test_process_content_sections_list(self):
        content_sections = [
            OrderedDict([
                ("tag_name", "list"),
                ("content", '<list><list-item><p>Item</p></list-item></list>'),
            ])
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "list")
        self.assertEqual(result[0].attr, {})
        self.assertEqual(result[0].content, '<list-item><p>Item</p></list-item>')

    def test_process_content_sections_disp_quote(self):
        content_sections = [
            OrderedDict([
                ("tag_name", "disp-quote"),
                ("content", '<disp-quote><p>Quotation</p></disp-quote>'),
            ])
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "disp-quote")
        self.assertEqual(result[0].attr, {})
        self.assertEqual(result[0].content, '<p>Quotation</p>')

    def test_process_content_sections_unknown(self):
        content_sections = [
            OrderedDict([
                ("tag_name", None),
                ("content", '<unknown />'),
            ])
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, None)
        self.assertEqual(result[0].attr, {})
        self.assertEqual(result[0].content, '<unknown />')

    def test_process_content_sections_maths(self):
        content_sections = [
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>First Paragraph</p>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p><disp-formula><mml:math alttext="\\beta_{V}"' +
                 ' xmlns:mml="http://www.w3.org/1998/Math/MathML" display="block">' +
                 '<mml:mrow><mml:msub><mml:mi>β</mml:mi><mml:mi>V</mml:mi></mml:msub>' +
                 '</mml:mrow></mml:math></disp-formula></p>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>Second Paragraph</p>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>Third Paragraph</p>'),
            ]),
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "p")
        self.assertEqual(result[0].content, (
            'First Paragraph<disp-formula><mml:math alttext="\\beta_{V}"' +
            ' xmlns:mml="http://www.w3.org/1998/Math/MathML" display="block">' +
            '<mml:mrow><mml:msub><mml:mi>β</mml:mi><mml:mi>V</mml:mi></mml:msub>' +
            '</mml:mrow></mml:math></disp-formula>Second Paragraph'))
        self.assertEqual(result[1].block_type, "p")
        self.assertEqual(result[1].content, (
            'Third Paragraph'))

    def test_process_content_sections_append(self):
        """test case for non-p following a disp-formula p"""
        content_sections = [
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>First Paragraph</p>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p><disp-formula></disp-formula></p>'),
            ]),
            OrderedDict([
                ("tag_name", "list"),
                ("content", '<list list-type="bullet"><list-item></list-item></list>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p><disp-formula></disp-formula></p>'),
            ]),
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "p")
        self.assertEqual(result[0].content, 'First Paragraph<disp-formula></disp-formula>')
        self.assertEqual(result[1].block_type, "list")
        self.assertEqual(result[1].attr, {"list-type": "bullet"})
        self.assertEqual(result[1].content, '<list-item></list-item>')
        self.assertEqual(result[2].block_type, "p")
        self.assertEqual(result[2].content, '<disp-formula></disp-formula>')

    def test_process_content_sections_p_italic(self):
        """test case for italic p"""
        content_sections = [
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>Regular paragraph.</p>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p><italic>First quoted paragraph.</italic></p>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p><italic>Second quoted paragraph.</italic></p>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>Response paragraph.</p>'),
            ]),
        ]
        result = build.process_content_sections(content_sections, self.prefs)
        self.assertEqual(result[0].block_type, 'p')
        self.assertEqual(result[0].content, 'Regular paragraph.')
        self.assertEqual(result[1].block_type, 'disp-quote')
        self.assertEqual(result[1].attr.get('content-type'), 'editor-comment')
        self.assertEqual(
            result[1].content, '<p>First quoted paragraph.</p><p>Second quoted paragraph.</p>')
        self.assertEqual(result[2].block_type, 'p')
        self.assertEqual(result[2].content, 'Response paragraph.')

    def test_process_content_sections_image_no_title(self):
        content_sections = [
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>&lt;Author response image 1&gt;</p>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>Next regular paragraph.</p>'),
            ]),
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, 'fig')
        self.assertEqual(result[0].content, (
            '<label>Author response image 1</label><graphic mimetype="image" xlink:href="todo" />'))
        self.assertEqual(result[1].block_type, 'p')

    def test_process_content_sections_video_no_title(self):
        content_sections = [
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>&lt;Author response video 1&gt;</p>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>Next regular paragraph.</p>'),
            ]),
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, 'media')
        self.assertEqual(result[0].content, (
            '<label>Author response video 1</label>'))
        self.assertEqual(result[0].attr, {
            'mimetype': 'video',
            'xlink:href': 'todo'
        })
        self.assertEqual(result[1].block_type, 'p')

    def test_process_content_sections_table_no_title(self):
        content_sections = [
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<bold>Author response Table 1.</bold>'),
            ]),
            OrderedDict([
                ("tag_name", "table"),
                ("content", '<table xmlns:mml="http://www.w3.org/1998/Math/MathML"></table>'),
            ]),
            OrderedDict([
                ("tag_name", "p"),
                ("content", '<p>Next regular paragraph.</p>'),
            ]),
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, 'table-wrap')
        self.assertEqual(result[0].content, (
            '<label>Author response Table 1.</label><table frame="hsides" rules="groups" />'))
        self.assertEqual(result[1].block_type, 'p')
