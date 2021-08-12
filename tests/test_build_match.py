# coding=utf-8

import unittest
from ddt import ddt, data
from letterparser import build


@ddt
class TestMatchPatterns(unittest.TestCase):
    @data(
        {"content": "", "expected": False},
        {"content": "&lt;Author response image 1&gt;", "expected": True},
        {"content": "content &lt;Author response image 1&gt;", "expected": False},
        {"content": "&lt;Decision letter image 666&gt;", "expected": True},
        {"content": "content &lt;Author response image 2.&gt;", "expected": False},
    )
    def test_match_fig_content_start(self, test_data):
        self.assertEqual(
            build.match_fig_content_start(test_data.get("content")),
            test_data.get("expected"),
        )

    @data(
        {"content": "", "expected": False},
        {"content": "&lt;Author response image 1 title/legend&gt;", "expected": True},
        {
            "content": "content &lt;Author response image 1 title/legend&gt;",
            "expected": False,
        },
        {"content": "&lt;Decision letter image 666 title/legend&gt;", "expected": True},
    )
    def test_match_fig_content_title_start(self, test_data):
        self.assertEqual(
            build.match_fig_content_title_start(test_data.get("content")),
            test_data.get("expected"),
        )

    @data(
        {"content": "", "expected": False},
        {"content": "&lt;Author response video 1&gt;", "expected": True},
        {"content": "content &lt;Author response video 1&gt;", "expected": False},
        {"content": "&lt;Decision letter video 666&gt;", "expected": True},
        {"content": "content &lt;Author response video 2.&gt;", "expected": False},
    )
    def test_match_video_content_start(self, test_data):
        self.assertEqual(
            build.match_video_content_start(test_data.get("content")),
            test_data.get("expected"),
        )

    @data(
        {"content": "", "expected": False},
        {"content": "<italic></italic>", "expected": True},
        {"content": "<italic> </italic> <italic> </italic>", "expected": True},
        {
            "content": (
                "<italic>2. The description ...</italic>"
                "<inline-formula><alternatives>"
                "<tex-math><![CDATA[- 2\\widetilde{v}]]></tex-math>"
                '<mml:math display="inline" xmlns:mml="http://www.w3.org/1998/Math/MathML">'
                "<mml:mrow><mml:mo>−</mml:mo><mml:mn>2</mml:mn>"
                '<mml:mover><mml:mi>v</mml:mi><mml:mo accent="true">∼</mml:mo></mml:mover>'
                "</mml:mrow></mml:math>"
                "</alternatives></inline-formula>"
                "<italic>.</italic>"
            ),
            "expected": True,
        },
    )
    def test_match_disp_quote_content(self, test_data):
        self.assertEqual(
            build.match_disp_quote_content(test_data.get("content")),
            test_data.get("expected"),
        )
