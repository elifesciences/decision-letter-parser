# coding=utf-8

import unittest
from letterparser import generate
from letterparser.objects import ContentBlock
from tests import helpers, read_fixture


def kitchen_sink_decision_letter():
    sub_article = helpers.base_decision_letter()

    preamble_block = ContentBlock("boxed-text")
    preamble_block.content_blocks.append(ContentBlock("p", (
        "In the interests of transparency, eLife includes the editorial decision letter" +
        " and accompanying author responses. A lightly edited version of the letter sent" +
        " to the authors after peer review is shown, indicating the most substantive concerns;" +
        " minor comments are not usually included.")))
    sub_article.content_blocks.append(preamble_block)

    sub_article.content_blocks.append(ContentBlock("p", (
        'Thank you for submitting your article "The eLife research article" for consideration' +
        " by <italic>eLife</italic>. Your article has been reviewed by three peer reviewers," +
        " one of whom, Joe Bloggs, is a member of our editorial board and also oversaw the" +
        " process as Senior editor. John Doe (peer reviewer) has agreed to reveal his identity.")))

    sub_article.content_blocks.append(ContentBlock("p", (
        "The reviewers have discussed the reviews with one another and the Reviewing Editor" +
        " has drafted this decision to help you prepare a revised submission.")))

    sub_article.content_blocks.append(ContentBlock("p", (
        "You need to make sure the XML structure you creates works on the display of the PMC" +
        " platform and also that there is enough information contained within the tagging to" +
        " generate a typeset PDF from the XML with no additional information provided.")))

    return sub_article


def kitchen_sink_author_response():
    sub_article = helpers.base_author_response()

    disp_quote_block = ContentBlock("disp-quote")
    disp_quote_block.attr["content-type"] = "editor-comment"
    disp_quote_block.content_blocks.append(ContentBlock("p", (
        "The reviewers have discussed the reviews with one another and the Reviewing Editor" +
        " has drafted this decision to help you prepare a revised submission.")))
    disp_quote_block.content_blocks.append(ContentBlock("p", (
        "You need to make sure the XML structure you creates works on the display of the PMC" +
        " platform and also that there is enough information contained within the tagging to" +
        "generate a typeset PDF from the XML with no additional information provided.")))
    sub_article.content_blocks.append(disp_quote_block)

    sub_article.content_blocks.append(ContentBlock("p", (
        "In response to this comment, we validated the XML against the DTD (JATS 1) each time" +
        " we made an update. We also regularly used the PMC validator to check our decisions" +
        " against display on the PMC site, see Author response image 1., Author response video 1" +
        " and Author response table 1.")))

    fig_block = ContentBlock("fig", (
        "<label>Author response image 1.</label><caption><p>Single figure: The header of an" +
        ' eLife article example on the HTML page.</p></caption><graphic mimetype="image"' +
        ' mime-subtype="tiff" xlink:href="elife-00666-resp-fig1.tif"/>'))
    fig_block.attr["id"] = "respfig1"
    fig_block.attr["position"] = "float"
    sub_article.content_blocks.append(fig_block)

    table_block = ContentBlock("table-wrap", (
        "<label>Author response Table 1.</label><caption><p>Author response table</p></caption>" +
        '<table frame="hsides" rules="groups"><thead>' +
        '<tr><th>Sample</th><th>Same</th><th>Difference more than 10%</th></tr>' +
        '</thead><tbody>' +
        '<tr><td>DKO1.cell.1</td><td>77.00%</td><td>6.90%</td></tr>' +
        '<tr><td>DKO1.cell.2</td><td>78.80%</td><td>7.20%</td></tr>' +
        '<tr><td>DKO1.cell.3</td><td>79.10%</td><td>6.70%</td></tr>' +
        '<tr><td>DKO1.exo.1</td><td>78.90%</td><td>6.50%</td></tr>' +
        '<tr><td>DKO1.exo.2</td><td>80.00%</td><td>5.80%</td></tr>' +
        '<tr><td>DKO1.exo.3</td><td>86.80%</td><td>2.30%</td></tr>' +
        '<tr><td>DKS8.cell.1</td><td>77.30%</td><td>7.80%</td></tr>' +
        '<tr><td>DKS8.cell.2</td><td>79.70%</td><td>6.70%</td></tr>' +
        '</tbody></table>'))
    table_block.attr["id"] = "resptable1"
    table_block.attr["position"] = "float"
    sub_article.content_blocks.append(table_block)

    media_block = ContentBlock("media", (
        "<label>Author response video 1.</label><caption><p>Caption and/or a title is required" +
        " for all author response assets</p></caption>"))
    media_block.attr["mimetype"] = "video"
    media_block.attr["mime-subtype"] = "mp4"
    media_block.attr["id"] = "respvideo1"
    media_block.attr["xlink:href"] = "elife-00666-resp-video1.mp4"
    sub_article.content_blocks.append(media_block)

    sub_article.content_blocks.append(ContentBlock("p", (
        "However, some decisions required some communication with PMC to discuss whether any of" +
        " our updates could be accomodated by them - during this review we aimed to reduce the" +
        " complexity of the XML structure and remove all formatting and bioler plate text" +
        " required for a PDF display format. We also produced buisness rules {Insert table}" +
        " in order to produce rules for the production systems and the website to follow. These" +
        " buisness rules also informed the basis for a set of Schematron rules for our" +
        " references.{Insert table}")))

    sub_article.content_blocks.append(ContentBlock("p", (
        "If an author referes to a reference in the response letter it is cross linked to the" +
        " reference in the reference list (Coyne and Orr, 1989), however, if it is a new" +
        " reference only cited in the decision letter or author response it is not added to the" +
        " main reference link and is just listed as free text, for example, Butcher et al, 2006." +
        " If the author provides the reference it can be added as free text to the end of the" +
        " letter, however, this is not a requirement.")))

    sub_article.content_blocks.append(ContentBlock("p", (
        "Adding some MathML to the sub-article.<inline-formula><mml:math><mml:mrow><mml:munder>" +
        '<mml:mo/><mml:mi>m</mml:mi></mml:munder><mml:mrow><mml:msub><mml:mover accent="true">' +
        "<mml:mi>p</mml:mi><mml:mo/></mml:mover><mml:mi>m</mml:mi></mml:msub><mml:mo>=</mml:mo>" +
        "<mml:mn>0</mml:mn></mml:mrow></mml:mrow></mml:math></inline-formula>")))

    sub_article.content_blocks.append(ContentBlock("p", (
        'May also contain a formula as a block<disp-formula><mml:math' +
        ' xmlns:mml="http://www.w3.org/1998/Math/MathML"><mml:mrow><mml:mi>ϕ</mml:mi>' +
        '<mml:mo>=</mml:mo><mml:msup><mml:mi>e</mml:mi><mml:mrow><mml:mo>−</mml:mo><mml:mfrac>' +
        '<mml:mtext mathvariant="normal">zFV</mml:mtext><mml:mtext mathvariant="normal">nRT' +
        '</mml:mtext></mml:mfrac></mml:mrow></mml:msup></mml:mrow></mml:math></disp-formula>')))

    list_block = ContentBlock("list", (
        "<list-item><p>'Contamination'</p>" +
        '<list list-type="roman-lower">' +
        '<list-item>' +
        '<p>Cell line <sup>superscript</sup><sub>subscript</sub> &amp; p&lt;0.001</p>' +
        '</list-item><list-item>' +
        '<p><italic>C. elegans</italic></p>' +
        '</list-item>' +
        '</list></list-item>'))
    list_block.attr["list-type"] = "order"
    sub_article.content_blocks.append(list_block)

    return sub_article


class TestGenerateKitchenSink(unittest.TestCase):

    def test_generate(self):
        """test creating kitchen sink XML output"""
        articles = [kitchen_sink_decision_letter(), kitchen_sink_author_response()]
        root = generate.generate(articles)
        pretty_xml = generate.output_xml(root, pretty=True, indent="    ")
        expected = read_fixture("kitchen_sink.xml", mode="rb")
        self.assertEqual(pretty_xml, expected)
