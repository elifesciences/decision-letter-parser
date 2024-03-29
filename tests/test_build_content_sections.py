# coding=utf-8

import unittest
from collections import OrderedDict
from letterparser import build


class TestProcessContentSections(unittest.TestCase):
    def setUp(self):
        # prefs for author_response sections
        self.prefs = OrderedDict()
        self.prefs["italic_to_disp_quote"] = True

    def test_process_content_sections(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "Hello!"),
                ]
            )
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "p")
        self.assertEqual(result[0].content, "Hello!")

    def test_process_content_sections_namespace(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    (
                        "content",
                        '<p xmlns:xlink="http://www.w3.org/1999/xlink">Hello!</p>',
                    ),
                ]
            )
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "p")
        self.assertEqual(result[0].content, "Hello!")

    def test_process_content_sections_table(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "table"),
                    ("content", "<table></table>"),
                ]
            )
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "table")
        self.assertEqual(result[0].content, "<table></table>")

    def test_process_content_sections_table_with_caption(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<italic>Italic paragraph.</italic>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<italic>Previous paragraph.</italic>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<bold>Author response Table 1.</bold>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    (
                        "content",
                        (
                            "&lt;Author response table 1 title/legend&gt;Author response table"
                            "&lt;/Author response table 1 title/legend&gt;"
                        ),
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "table"),
                    (
                        "content",
                        '<table xmlns:mml="http://www.w3.org/1998/Math/MathML"></table>',
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<italic>Next paragraph.</italic>"),
                ]
            ),
        ]
        result = build.process_content_sections(content_sections, self.prefs)
        self.assertEqual(result[0].block_type, "disp-quote")
        self.assertEqual(
            result[0].content, "<p>Italic paragraph.</p><p>Previous paragraph.</p>"
        )
        self.assertEqual(result[1].block_type, "table-wrap")
        self.assertEqual(
            result[1].content,
            (
                "<label>Author response Table 1.</label>"
                "<caption><title>Author response table</title></caption>"
                '<table frame="hsides" rules="groups" />'
            ),
        )
        self.assertEqual(result[2].block_type, "disp-quote")
        self.assertEqual(result[2].content, "<p>Next paragraph.</p>")

    def test_process_content_sections_table_disp_quote(self):
        """test for previous block is a disp-quote type"""
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<italic>Paragraph.</italic>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<bold>Author response Table 1.</bold>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    (
                        "content",
                        (
                            "&lt;Author response table 1 title/legend&gt;Author response table"
                            "&lt;/Author response table 1 title/legend&gt;"
                        ),
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "table"),
                    (
                        "content",
                        '<table xmlns:mml="http://www.w3.org/1998/Math/MathML"></table>',
                    ),
                ]
            ),
        ]
        result = build.process_content_sections(content_sections, self.prefs)
        self.assertEqual(result[0].block_type, "disp-quote")
        self.assertEqual(result[1].block_type, "table-wrap")
        self.assertEqual(
            result[1].content,
            (
                "<label>Author response Table 1.</label>"
                "<caption><title>Author response table</title></caption>"
                '<table frame="hsides" rules="groups" />'
            ),
        )

    def test_process_content_sections_table_paragraph_sandwich(self):
        """test for edge case of table with regular paragraphs on either side"""
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "Paragraph before."),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<bold>Author response Table 1.</bold>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    (
                        "content",
                        (
                            "&lt;Author response table 1 title/legend&gt;Author response table"
                            "&lt;/Author response table 1 title/legend&gt;"
                        ),
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "table"),
                    (
                        "content",
                        '<table xmlns:mml="http://www.w3.org/1998/Math/MathML"></table>',
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "Paragraph after."),
                ]
            ),
        ]
        result = build.process_content_sections(content_sections, self.prefs)
        self.assertEqual(result[0].block_type, "p")
        self.assertEqual(result[0].content, "Paragraph before.")
        self.assertEqual(result[1].block_type, "table-wrap")
        self.assertEqual(
            result[1].content,
            (
                "<label>Author response Table 1.</label>"
                "<caption><title>Author response table</title></caption>"
                '<table frame="hsides" rules="groups" />'
            ),
        )
        self.assertEqual(result[2].block_type, "p")
        self.assertEqual(result[2].content, "Paragraph after.")

    def test_process_content_sections_list(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "list"),
                    ("content", "<list><list-item><p>Item</p></list-item></list>"),
                ]
            )
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "list")
        self.assertEqual(result[0].attr, {})
        self.assertEqual(result[0].content, "<list-item><p>Item</p></list-item>")

    def test_process_content_sections_disp_quote(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "disp-quote"),
                    ("content", "<disp-quote><p>Quotation</p></disp-quote>"),
                ]
            )
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "disp-quote")
        self.assertEqual(result[0].attr, {})
        self.assertEqual(result[0].content, "<p>Quotation</p>")

    def test_process_content_sections_unknown(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", None),
                    ("content", "<unknown />"),
                ]
            )
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, None)
        self.assertEqual(result[0].attr, {})
        self.assertEqual(result[0].content, "<unknown />")

    def test_process_content_sections_maths(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>First Paragraph</p>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    (
                        "content",
                        '<p><disp-formula><mml:math alttext="\\beta_{V}"'
                        + ' xmlns:mml="http://www.w3.org/1998/Math/MathML" display="block">'
                        + "<mml:mrow><mml:msub><mml:mi>β</mml:mi><mml:mi>V</mml:mi></mml:msub>"
                        + "</mml:mrow></mml:math></disp-formula></p>",
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>Second Paragraph</p>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>Third Paragraph</p>"),
                ]
            ),
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "p")
        self.assertEqual(
            result[0].content,
            (
                'First Paragraph<disp-formula><mml:math alttext="\\beta_{V}"'
                + ' xmlns:mml="http://www.w3.org/1998/Math/MathML" display="block">'
                + "<mml:mrow><mml:msub><mml:mi>β</mml:mi><mml:mi>V</mml:mi></mml:msub>"
                + "</mml:mrow></mml:math></disp-formula>Second Paragraph"
            ),
        )
        self.assertEqual(result[1].block_type, "p")
        self.assertEqual(result[1].content, ("Third Paragraph"))

    def test_process_content_sections_append(self):
        """test case for non-p following a disp-formula p"""
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>First Paragraph</p>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p><disp-formula></disp-formula></p>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "list"),
                    (
                        "content",
                        '<list list-type="bullet"><list-item></list-item></list>',
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p><disp-formula></disp-formula></p>"),
                ]
            ),
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "p")
        self.assertEqual(
            result[0].content, "First Paragraph<disp-formula></disp-formula>"
        )
        self.assertEqual(result[1].block_type, "list")
        self.assertEqual(result[1].attr, {"list-type": "bullet"})
        self.assertEqual(result[1].content, "<list-item></list-item>")
        self.assertEqual(result[2].block_type, "p")
        self.assertEqual(result[2].content, "<disp-formula></disp-formula>")

    def test_process_content_sections_p_italic(self):
        """test case for italic p"""
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>Regular paragraph.</p>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p><italic>First quoted paragraph.</italic></p>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p><italic>Second quoted paragraph.</italic></p>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>Response paragraph.</p>"),
                ]
            ),
        ]
        result = build.process_content_sections(content_sections, self.prefs)
        self.assertEqual(result[0].block_type, "p")
        self.assertEqual(result[0].content, "Regular paragraph.")
        self.assertEqual(result[1].block_type, "disp-quote")
        self.assertEqual(result[1].attr.get("content-type"), "editor-comment")
        self.assertEqual(
            result[1].content,
            "<p>First quoted paragraph.</p><p>Second quoted paragraph.</p>",
        )
        self.assertEqual(result[2].block_type, "p")
        self.assertEqual(result[2].content, "Response paragraph.")

    def test_process_content_sections_image(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "disp-quote"),
                    (
                        "content",
                        "<p>First editor comment.</p><p>An extra paragraph</p>",
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>First <italic>paragraph</italic>.</p>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>&lt;Author response image 1&gt;</p>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    (
                        "content",
                        (
                            "<p>&lt;Author response image 1 title/legend&gt;"
                            "<bold>Author response image 1.</bold>"
                            " Title up to first full stop. Caption <sup>2+</sup> calculated using"
                            "&lt;/Author response image 1 title/legend&gt;</p>"
                        ),
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "disp-quote"),
                    ("content", "<p>Editor comment paragraph.</p>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>Paragraph.</p>"),
                ]
            ),
        ]
        result = build.process_content_sections(content_sections, prefs=self.prefs)
        self.assertEqual(result[0].block_type, "disp-quote")
        self.assertEqual(result[1].block_type, "p")
        self.assertEqual(result[2].block_type, "fig")
        self.assertEqual(
            result[2].content,
            (
                "<label>Author response image 1.</label>"
                "<caption><title>Title up to first full stop.</title>"
                "<p>Caption <sup>2+</sup> calculated using</p></caption>"
                '<graphic mimetype="image" xlink:href="todo" />'
            ),
        )
        self.assertEqual(result[3].block_type, "disp-quote")

    def test_process_content_sections_image_no_title(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>&lt;Author response image 1&gt;</p>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>Next regular paragraph.</p>"),
                ]
            ),
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "fig")
        self.assertEqual(
            result[0].content,
            (
                '<label>Author response image 1</label><graphic mimetype="image" xlink:href="todo" />'
            ),
        )
        self.assertEqual(result[1].block_type, "p")

    def test_process_content_sections_image_no_title_editor_comment(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>&lt;Author response image 2&gt;</p>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p><italic>Editor comment paragraph.</italic></p>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>Next regular paragraph.</p>"),
                ]
            ),
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "fig")
        self.assertEqual(
            result[0].content,
            (
                '<label>Author response image 2</label><graphic mimetype="image" xlink:href="todo" />'
            ),
        )
        self.assertEqual(result[1].block_type, "disp-quote")
        self.assertEqual(result[1].content, "<p>Editor comment paragraph.</p>")
        self.assertEqual(result[2].block_type, "p")
        self.assertEqual(result[2].content, "Next regular paragraph.")

    def test_process_content_sections_video_no_title(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>&lt;Author response video 1&gt;</p>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>Next regular paragraph.</p>"),
                ]
            ),
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "media")
        self.assertEqual(result[0].content, ("<label>Author response video 1</label>"))
        self.assertEqual(result[0].attr, {"mimetype": "video", "xlink:href": "todo"})
        self.assertEqual(result[1].block_type, "p")

    def test_process_content_sections_table_no_title(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<bold>Author response Table 1.</bold>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "table"),
                    (
                        "content",
                        '<table xmlns:mml="http://www.w3.org/1998/Math/MathML"></table>',
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>Next regular paragraph.</p>"),
                ]
            ),
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "table-wrap")
        self.assertEqual(
            result[0].content,
            (
                '<label>Author response Table 1.</label><table frame="hsides" rules="groups" />'
            ),
        )
        self.assertEqual(result[1].block_type, "p")

    def test_process_content_sections_table_no_title_non_bold(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "&lt;Author response Table 1&gt;"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "table"),
                    (
                        "content",
                        '<table xmlns:mml="http://www.w3.org/1998/Math/MathML"></table>',
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>Next regular paragraph.</p>"),
                ]
            ),
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "table-wrap")
        self.assertEqual(
            result[0].content,
            (
                '<label>Author response Table 1</label><table frame="hsides" rules="groups" />'
            ),
        )
        self.assertEqual(result[1].block_type, "p")

    def test_process_content_sections_table_angle_brackets(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "&lt;Author response Table 1&gt;"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    (
                        "content",
                        (
                            "&lt;Author response table 1 title/legend&gt;"
                            "<bold>Author response Table 1.</bold>"
                            "Coating protocols used to test gliding motility of "
                            "sporozoites on different substrates."
                        ),
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    (
                        "content",
                        (
                            "Gliding assays were performed in 96-well plates and wells were "
                            "coated with heparin, ICAM-I, laminin, fibronectin and collagen according to "
                            "the following protocols (Bilsland, Diamond and Springer, 1994; "
                            "Gao<italic>et al.,</italic>2011). "
                            "&lt;/Author response table 1 title/legend&gt;"
                        ),
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "table"),
                    (
                        "content",
                        '<table xmlns:mml="http://www.w3.org/1998/Math/MathML"></table>',
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>Next regular paragraph.</p>"),
                ]
            ),
        ]
        result = build.process_content_sections(content_sections)
        print(result[0].content)
        self.assertEqual(result[0].block_type, "table-wrap")
        self.assertEqual(
            result[0].content,
            (
                "<label>Author response Table 1.</label><caption><title>"
                "Coating protocols used to test gliding motility of sporozoites on "
                "different substrates.</title><p>Gliding assays were performed in 96-well "
                "plates and wells were coated with heparin, ICAM-I, laminin, fibronectin and "
                "collagen according to the following protocols "
                "(Bilsland, Diamond and Springer, 1994; Gao<italic>et al.,</italic>2011). "
                '</p></caption><table frame="hsides" rules="groups" />'
            ),
        )
        self.assertEqual(result[1].block_type, "p")

    def test_process_content_sections_many_images_no_title(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>&lt;Author response image 1&gt;</p>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>&lt;Author response image 2&gt;</p>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>&lt;Author response image 3&gt;</p>"),
                ]
            ),
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "fig")
        self.assertEqual(
            result[0].content,
            (
                '<label>Author response image 1</label><graphic mimetype="image" xlink:href="todo" />'
            ),
        )
        self.assertEqual(result[1].block_type, "fig")
        self.assertEqual(
            result[1].content,
            (
                '<label>Author response image 2</label><graphic mimetype="image" xlink:href="todo" />'
            ),
        )
        self.assertEqual(result[2].block_type, "fig")
        self.assertEqual(
            result[2].content,
            (
                '<label>Author response image 3</label><graphic mimetype="image" xlink:href="todo" />'
            ),
        )

    def test_process_content_sections_two_images(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>&lt;Author response image 1&gt;</p>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    (
                        "content",
                        (
                            "<p>&lt;Author response image 1 title/legend&gt;"
                            "<bold>Author response image 1.</bold>"
                            " Title up to first full stop. Caption <sup>2+</sup> calculated."
                            "&lt;/Author response image 1 title/legend&gt;</p>"
                        ),
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<p>&lt;Author response image 2&gt;</p>"),
                ]
            ),
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "fig")
        self.assertEqual(
            result[0].content,
            (
                "<label>Author response image 1.</label><caption><title>Title up to first full stop."
                "</title><p>Caption <sup>2+</sup> calculated.</p></caption>"
                '<graphic mimetype="image" xlink:href="todo" />'
            ),
        )
        self.assertEqual(result[1].block_type, "fig")
        self.assertEqual(
            result[1].content,
            (
                '<label>Author response image 2</label><graphic mimetype="image" xlink:href="todo" />'
            ),
        )

    def test_process_content_sections_fig_then_table(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "&lt;Author response image 1&gt;"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "<bold>Author response table 1</bold>"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "table"),
                    ("content", "<table></table>"),
                ]
            ),
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "fig")
        self.assertEqual(
            result[0].content,
            (
                '<label>Author response image 1</label><graphic mimetype="image" xlink:href="todo" />'
            ),
        )
        self.assertEqual(result[1].block_type, "table-wrap")
        self.assertEqual(
            result[1].content,
            (
                '<label>Author response table 1</label><table frame="hsides" rules="groups" />'
            ),
        )

    def test_process_content_sections_fig_then_media(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "&lt;Author response image 1&gt;"),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "&lt;Author response video 1&gt;"),
                ]
            ),
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "fig")
        self.assertEqual(
            result[0].content,
            (
                '<label>Author response image 1</label><graphic mimetype="image" xlink:href="todo" />'
            ),
        )
        self.assertEqual(result[1].block_type, "media")
        self.assertEqual(result[1].content, ("<label>Author response video 1</label>"))
        self.assertEqual(result[1].attr, {"mimetype": "video", "xlink:href": "todo"})

    def test_process_content_sections_p_then_italic_inline_formula(self):
        content_sections = [
            OrderedDict(
                [
                    ("tag_name", "p"),
                    (
                        "content",
                        (
                            "The sign convention ... "
                            "<inline-formula><alternatives>"
                            "<tex-math><![CDATA[{\\widetilde{v}}_{i}]]></tex-math>"
                            '<mml:math display="inline" '
                            'xmlns:mml="http://www.w3.org/1998/Math/MathML">'
                            "<mml:msub><mml:mover><mml:mi>v</mml:mi>"
                            '<mml:mo accent="true">∼</mml:mo>'
                            "</mml:mover><mml:mi>i</mml:mi></mml:msub></mml:math>"
                            "</alternatives></inline-formula> remains the same."
                        ),
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    (
                        "content",
                        (
                            "<italic>2. The description ...</italic> "
                            "<inline-formula><alternatives>"
                            "<tex-math><![CDATA[{2\\widetilde{v}}_{i}]]></tex-math>"
                            '<mml:math display="inline" '
                            'xmlns:mml="http://www.w3.org/1998/Math/MathML">'
                            "<mml:msub><mml:mrow><mml:mn>2</mml:mn><mml:mover><mml:mi>v</mml:mi>"
                            '<mml:mo accent="true">∼</mml:mo>'
                            "</mml:mover></mml:mrow><mml:mi>i</mml:mi></mml:msub></mml:math>"
                            "</alternatives></inline-formula> "
                            "<italic>-1? ...</italic> "
                            "<inline-formula><alternatives>"
                            "<tex-math><![CDATA[{2\\widetilde{v}}_{i}]]></tex-math>"
                            '<mml:math display="inline" '
                            'xmlns:mml="http://www.w3.org/1998/Math/MathML">'
                            "<mml:msub><mml:mrow><mml:mn>2</mml:mn><mml:mover><mml:mi>v</mml:mi>"
                            '<mml:mo accent="true">∼</mml:mo>'
                            "</mml:mover></mml:mrow><mml:mi>i</mml:mi></mml:msub></mml:math>"
                            "</alternatives></inline-formula><italic>.</italic>"
                        ),
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("tag_name", "p"),
                    ("content", "We thank the reviewer ...."),
                ]
            ),
        ]
        result = build.process_content_sections(content_sections)
        self.assertEqual(result[0].block_type, "p")
        self.assertEqual(
            result[0].content,
            (
                "The sign convention ... "
                "<inline-formula><alternatives>"
                "<tex-math><![CDATA[{\\widetilde{v}}_{i}]]></tex-math>"
                '<mml:math display="inline" xmlns:mml="http://www.w3.org/1998/Math/MathML">'
                "<mml:msub><mml:mover><mml:mi>v</mml:mi>"
                '<mml:mo accent="true">∼</mml:mo>'
                "</mml:mover><mml:mi>i</mml:mi></mml:msub></mml:math>"
                "</alternatives></inline-formula> remains the same."
            ),
        )
        self.assertEqual(result[1].block_type, "p")
        self.assertEqual(
            result[1].content,
            (
                "<italic>2. The description ...</italic> "
                "<inline-formula><alternatives>"
                "<tex-math><![CDATA[{2\\widetilde{v}}_{i}]]></tex-math>"
                '<mml:math display="inline" xmlns:mml="http://www.w3.org/1998/Math/MathML">'
                "<mml:msub><mml:mrow><mml:mn>2</mml:mn><mml:mover><mml:mi>v</mml:mi>"
                '<mml:mo accent="true">∼</mml:mo>'
                "</mml:mover></mml:mrow><mml:mi>i</mml:mi></mml:msub></mml:math>"
                "</alternatives></inline-formula> "
                "<italic>-1? ...</italic> "
                "<inline-formula><alternatives>"
                "<tex-math><![CDATA[{2\\widetilde{v}}_{i}]]></tex-math>"
                '<mml:math display="inline" xmlns:mml="http://www.w3.org/1998/Math/MathML">'
                "<mml:msub><mml:mrow><mml:mn>2</mml:mn><mml:mover><mml:mi>v</mml:mi>"
                '<mml:mo accent="true">∼</mml:mo>'
                "</mml:mover></mml:mrow><mml:mi>i</mml:mi></mml:msub></mml:math>"
                "</alternatives></inline-formula><italic>.</italic>"
            ),
        )
        self.assertEqual(result[2].block_type, "p")
        self.assertEqual(result[2].content, ("We thank the reviewer ...."))
