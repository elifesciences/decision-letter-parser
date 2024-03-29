import unittest
from letterparser import parse


class TestConvertBreakTags(unittest.TestCase):
    def test_convert_break_tags_simple(self):
        jats_content = "<p>One.<break /><break />Two.</p>"
        expected = "<p>One.</p><p>Two.</p>"
        result = parse.convert_break_tags(jats_content)
        self.assertEqual(result, expected)

    def test_convert_break_tags_open_italic(self):
        jats_content = (
            "<p><italic>One</italic> <italic>two.<break /><break />3.</italic></p>"
        )
        expected = "<p><italic>One</italic> <italic>two.</italic></p><p><italic>3.</italic></p>"
        result = parse.convert_break_tags(jats_content)
        self.assertEqual(result, expected)

    def test_convert_break_tags_even_tag_count(self):
        jats_content = (
            "<p><italic>One.<break /><break />A </italic><italic>half."
            + "<break /><break />Two.</italic></p>"
        )
        expected = (
            "<p><italic>One.</italic></p><p><italic>A </italic><italic>half.</italic></p>"
            + "<p><italic>Two.</italic></p>"
        )
        result = parse.convert_break_tags(jats_content)
        self.assertEqual(result, expected)

    def test_convert_break_tags_running_italic(self):
        jats_content = (
            "<p><italic>One.<break /><break />Keeps.<break /><break />"
            + "Going.</italic></p>"
        )
        expected = (
            "<p><italic>One.</italic></p><p><italic>Keeps.</italic></p>"
            + "<p><italic>Going.</italic></p>"
        )
        result = parse.convert_break_tags(jats_content)
        self.assertEqual(result, expected)

    def test_convert_break_tags_italic_sandwich(self):
        jats_content = "<p>Bread.<break /><italic><break />Cheese.</italic></p>"
        expected = "<p>Bread.</p><p><italic>Cheese.</italic></p>"
        result = parse.convert_break_tags(jats_content)
        self.assertEqual(result, expected)

    def test_convert_break_tags_two_italic_tags(self):
        jats_content = (
            "<p><bold>Author response</bold></p><break /><break /><p><italic>A series of"
            " important changes is requested before the manuscript could be</italic> <italic>"
            "considered for publication in eLife.<break /><break />1) The authors need to do...."
            "</italic></p><break /><break /><p>Plain paragraph.</p>"
        )
        expected = (
            "<p><bold>Author response</bold></p><p><italic>A series of important changes is"
            " requested before the manuscript could be</italic> <italic>considered for"
            " publication in eLife.</italic></p><p><italic>1) The authors need to do...."
            "</italic></p><p>Plain paragraph.</p>"
        )
        result = parse.convert_break_tags(jats_content)
        self.assertEqual(result, expected)

    def test_convert_break_tags_table_td(self):
        jats_content = (
            "<table><tr><td>BI-167107 (agonist)<break /><break />"
            "G<sub>s</sub> (G protein)</td></tr></table>"
        )
        expected = (
            "<table><tr><td>BI-167107 (agonist)<break />"
            "G<sub>s</sub> (G protein)</td></tr></table>"
        )
        result = parse.convert_break_tags(jats_content)
        self.assertEqual(result, expected)

    def test_convert_break_tags_italic_table_edge_case(self):
        jats_content = (
            "<p>We have plotted ....</p><p><italic>2) The end of ....<break /><break />"
            "&quot;if the overlap ....&quot;</italic></p><p><italic>However, green dashed "
            "line ....</italic></p><p>We agree with ....</p>"
            "<table><tbody><tr><td></td></tr></tbody></table>"
        )
        expected = (
            "<p>We have plotted ....</p><p><italic>2) The end of ....</italic></p>"
            "<p><italic>&quot;if the overlap ....&quot;</italic></p>"
            "<p><italic>However, green dashed line ....</italic></p>"
            "<p>We agree with ....</p>"
            "<table><tbody><tr><td></td></tr></tbody></table>"
        )
        result = parse.convert_break_tags(jats_content)
        self.assertEqual(result, expected)

    def test_convert_break_tags_disp_quote_edge_case(self):
        jats_content = (
            "<p><italic>Italic paragraph</italic></p>"
            "<disp-quote><p>Disp quote paragraph.</p></disp-quote>"
        )
        expected = (
            "<p><italic>Italic paragraph</italic></p>"
            "<disp-quote><p>Disp quote paragraph.</p></disp-quote>"
        )
        result = parse.convert_break_tags(jats_content)
        self.assertEqual(result, expected)

    def test_convert_break_tags_list_edge_case(self):
        jats_content = (
            "<p><italic>Italic paragraph</italic></p>"
            '<list list-type="order"><list-item><p>One</p></list-item></list>'
        )
        expected = (
            "<p><italic>Italic paragraph</italic></p>"
            '<list list-type="order"><list-item><p>One</p></list-item></list>'
        )
        result = parse.convert_break_tags(jats_content)
        self.assertEqual(result, expected)
