# coding=utf-8

import re
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from collections import OrderedDict
import elifearticle.utils as eautils
from elifearticle.article import Article, ContentBlock, RelatedArticle
from letterparser import parse, utils
from letterparser.conf import raw_config, parse_raw_config


def default_preamble(config):
    if config and config.get("preamble"):
        return OrderedDict(
            [
                ("section_type", "preamble"),
                ("content", config.get("preamble")),
            ]
        )
    return None


def build_articles(jats_content, file_name=None, config=None):
    sections = parse.sections(jats_content)

    if not config:
        config = parse_raw_config(raw_config(None))

    articles = []
    preamble_section = None
    id_count = 1

    # get a sciety link from the first preamble section
    related_material = None
    for preamble_section in [
        section for section in sections if section.get("section_type") == "preamble"
    ]:
        sciety_link_match_pattern = re.compile(
            r'.*xlink:href="(https://sciety.org/.*?)".*'
        )
        sciety_match = sciety_link_match_pattern.match(preamble_section.get("content"))
        if sciety_match:
            related_material = RelatedArticle()
            related_material.xlink_href = sciety_match.group(1)
            related_material.ext_link_type = "continued-by"
            break

    # filter a list of decision letter sections to check against later
    decision_letter_sections = [
        section
        for section in sections
        if section.get("section_type") == "decision_letter"
    ]

    # add the editor evaluation section first, if present
    if [
        section
        for section in sections
        if section.get("section_type") == "editors_evaluation"
    ]:
        id_count = 0

    for section in sections:
        if section.get("section_type") == "preamble":
            preamble_section = section
            continue

        # use sa2 as the id value for the first author response if there is no decision letter
        if (
            id_count == 1
            and section.get("section_type") == "author_response"
            and not decision_letter_sections
        ):
            id_count += 1

        if not preamble_section:
            preamble_section = default_preamble(config)

        id_value = "sa%s" % id_count

        # set the DOI, if possible
        manuscript = utils.manuscript_from_file_name(file_name)
        doi = build_doi(file_name, id_value, config)

        if section.get("section_type") == "editors_evaluation":
            article = build_editors_evaluation(
                section, config, id_value, doi, manuscript
            )
            if related_material:
                article.related_articles = [related_material]
        elif section.get("section_type") == "decision_letter":
            article = build_decision_letter(
                section, config, preamble_section, id_value, doi, manuscript
            )
        else:
            article = build_sub_article(
                section, config, "reply", id_value, doi, manuscript
            )
        articles.append(article)
        # reset the counter
        id_count += 1
        # reset the preamble section
        preamble_section = None

    return articles


def build_doi(file_name, id_value, config):
    if file_name and config and config.get("doi_pattern"):
        return config.get("doi_pattern").format(
            manuscript=utils.manuscript_from_file_name(file_name), id=id_value
        )
    return None


def build_editors_evaluation(section, config, id_value=None, doi=None, manuscript=None):
    return build_sub_article(
        section, config, "editor-report", id_value, doi, manuscript
    )


def build_decision_letter(
    section, config, preamble_section=None, id_value=None, doi=None, manuscript=None
):
    article = build_sub_article(
        section, config, "decision-letter", id_value, doi, manuscript
    )
    # process the preabmle section
    if preamble_section:
        preamble_section = trim_section_heading(preamble_section)
        preamble_block = ContentBlock("boxed-text", preamble_section.get("content"))
        article.content_blocks = [preamble_block] + article.content_blocks
    return article


def build_sub_article(
    section, config, article_type=None, id_value=None, doi=None, manuscript=None
):
    article = Article(doi)
    article.id = id_value
    article.manuscript = manuscript
    if article_type:
        article.article_type = article_type
    # add the content
    article.content_blocks = []
    set_title(article)
    set_content_blocks(article, section)
    # set any figure or video file names
    fig_num = 1
    video_num = 1
    for content_block in article.content_blocks:
        if content_block.block_type == "fig":
            image_file_name = config.get("fig_filename_pattern").format(
                manuscript=manuscript, id_value=id_value, num=fig_num
            )
            href = 'xlink:href="{image_file_name}"'.format(
                image_file_name=image_file_name
            )
            content_block.content = re.sub(
                r'(<graphic.*?)xlink:href=".*?"', r"\1%s" % href, content_block.content
            )
            fig_num += 1
        elif content_block.block_type == "media":
            # set video file names
            video_file_name = config.get("video_filename_pattern").format(
                manuscript=manuscript, id_value=id_value, num=video_num
            )
            content_block.attr["xlink:href"] = video_file_name
            video_num += 1

    return article


def set_title(article):
    """set the article title"""
    # for now use boilerplate values based on the article_type
    title_map = {
        "editor-report": "Editor's evaluation",
        "decision-letter": "Decision letter",
        "reply": "Author response",
    }
    article.title = title_map.get(article.article_type)


def trim_section_heading(section):
    for fragment in parse.SECTION_MAP.values():
        match = r"^" + fragment
        section["content"] = re.sub(match, "", section.get("content"))
    return section


def set_content_blocks(article, section):
    """set the body content blocks"""
    # set prefs based on the section type
    prefs = OrderedDict()
    prefs["italic_to_disp_quote"] = bool(
        section.get("section_type") == "author_response"
    )

    # trim away the section heading
    section = trim_section_heading(section)
    # split into content sections
    content_sections = split_content_sections(section)
    # profile and process into content blocks
    content_blocks = process_content_sections(content_sections, prefs)
    # add to the article
    article.content_blocks = content_blocks


def split_content_sections(section):
    """split first child level tags into content parts"""
    content_sections = []
    # register namespaces
    for prefix, uri in utils.XML_NAMESPACE_MAP.items():
        ElementTree.register_namespace(prefix, uri)
    # parse content
    xml_string = "<root %s>%s</root>" % (
        utils.reparsing_namespaces(utils.XML_NAMESPACE_MAP),
        section.get("content"),
    )
    section_xml = ElementTree.fromstring(xml_string)

    # clean the math alternatives here
    section_xml = clean_math_alternatives(section_xml)

    for block_tag in section_xml.findall("./*"):
        if block_tag.tag in ["list", "p", "table", "disp-quote"]:
            # add p tags from disp-quote blocks
            if block_tag.tag == "disp-quote":
                for p_tag in block_tag.findall("./p"):
                    append_tag_to_sections(content_sections, p_tag)
            else:
                append_tag_to_sections(content_sections, block_tag)
    return content_sections


def append_tag_to_sections(sections, tag):
    content_section = OrderedDict()
    rough_string = element_to_string(tag)
    content_section["tag_name"] = tag.tag
    content_section["content"] = rough_string
    sections.append(content_section)


def element_to_string(tag):
    rough_string = ElementTree.tostring(tag, "utf8").decode("utf8")
    rough_string = rough_string.replace("<?xml version='1.0' encoding='utf8'?>", "")
    rough_string = rough_string.lstrip("\n")
    return rough_string


def clean_math_alternatives(section_xml):
    """use mml:math from the <alternatives> tag"""
    for formula_tag in section_xml.findall(".//disp-formula") + section_xml.findall(
        ".//inline-formula"
    ):
        mml_tag = formula_tag.find(
            ".//{http://www.w3.org/1998/Math/MathML}math", utils.XML_NAMESPACE_MAP
        )
        tex_math_tag = formula_tag.find(".//tex-math")
        mml_tag.set("alttext", tex_math_tag.text)
        alt_tag = formula_tag.find("./alternatives")
        formula_tag.remove(alt_tag)
        formula_tag.append(mml_tag)
    return section_xml


def extract_label_title_content(content):
    title_content = None
    content_content = None

    # possibly only label provided
    bracket_matches = content.count("&lt;")
    if content.startswith("&lt;") and bracket_matches == 1:
        label_parts_match = re.match(r"^\&lt;(.*?)\&gt;$", content)
        label_content = label_parts_match.group(1)
        return label_content, "", ""

    parts_match = re.findall(r"<bold>(.*?)</bold>(.*)$", content)
    label_content = parts_match[0][0]
    remainder = "".join(parts_match[0][1:])
    title_parts = remainder.split(".")
    # if the first part contains an mml tag, it is probably too complicated to process as parts
    if "<mml" in title_parts[0]:
        title_parts = [remainder]
    title_label_match = r"^(.*)\&lt;.*\&gt;$"
    if len(title_parts) == 1:
        content_match = re.match(title_label_match, title_parts[0])
        title_content = content_match.group(1).lstrip()
    else:
        # check for nested italic tags
        title_content = ""
        content_remainders = []
        for title_part in title_parts:
            if not title_content:
                title_content += title_part + "."
                continue
            open_tag_count = title_content.count(utils.open_tag("italic"))
            close_tag_count = title_content.count(utils.close_tag("italic"))
            open_bold_tag_count = title_content.count(utils.open_tag("bold"))
            close_bold_tag_count = title_content.count(utils.close_tag("bold"))
            open_ext_link_tag_count = title_content.count(
                utils.open_tag("ext-link").rstrip(">")
            )
            close_ext_link_tag_count = title_content.count(utils.close_tag("ext-link"))
            if (
                open_tag_count != close_tag_count
                or open_bold_tag_count != close_bold_tag_count
                or open_ext_link_tag_count != close_ext_link_tag_count
            ):
                title_content += title_part + "."
            else:
                content_remainders.append(title_part)
        title_content = title_content.lstrip()
        content_remainder = ".".join(content_remainders)
        # strip the title / legend close tag
        content_match = re.match(title_label_match, content_remainder)
        if content_match:
            content_content = content_match.group(1).lstrip()

    return label_content, title_content, content_content


def build_fig(content):
    """parse content into individual elements of a figure"""
    fig_c = OrderedDict()
    fig_c["label"], fig_c["title"], fig_c["content"] = extract_label_title_content(
        content
    )
    return fig_c


def fig_element(label, title, content):
    """populate an XML Element for a fig"""
    fig_tag = Element("fig")
    label_tag = SubElement(fig_tag, "label")
    label_tag.text = label

    if title or content:
        caption_tag = SubElement(fig_tag, "caption")

    if title:
        utils.append_to_parent_tag(caption_tag, "title", title, utils.XML_NAMESPACE_MAP)

    # append content as a p tag in the caption
    if content:
        utils.append_to_parent_tag(caption_tag, "p", content, utils.XML_NAMESPACE_MAP)

    graphic_tag = SubElement(fig_tag, "graphic")
    graphic_tag.set("mimetype", "image")
    graphic_tag.set("xlink:href", "todo")
    return fig_tag


def fig_element_to_string(tag):
    rough_string = element_to_string(tag)
    return utils.clean_portion(rough_string, "fig")


def media_element(label, title, content, mimetype="video"):
    """populate a media XML Element for a video"""
    media_tag = Element("media")
    media_tag.set("mimetype", mimetype)
    media_tag.set("xlink:href", "todo")

    label_tag = SubElement(media_tag, "label")
    label_tag.text = label

    if title or content:
        caption_tag = SubElement(media_tag, "caption")
        if title:
            utils.append_to_parent_tag(
                caption_tag, "title", title, utils.XML_NAMESPACE_MAP
            )

        # append content as a p tag in the caption
        if content:
            utils.append_to_parent_tag(
                caption_tag, "p", content, utils.XML_NAMESPACE_MAP
            )

    return media_tag


def disp_quote_element(content):
    """wrap non-italicised content into disp-quote tag"""
    root_tag = Element("disp-quote")

    if content:
        utils.append_to_parent_tag(
            root_tag, "disp-quote", content, utils.XML_NAMESPACE_MAP
        )

    return root_tag[0]


def media_element_to_string(tag):
    rough_string = element_to_string(tag)
    return utils.clean_portion(rough_string, "media")


def disp_quote_element_to_string(tag):
    rough_string = element_to_string(tag)
    return utils.clean_portion(rough_string, "disp-quote")


def table_wrap_element_to_string(tag):
    rough_string = element_to_string(tag)
    return utils.clean_portion(rough_string, "table-wrap")


def build_table_wrap(content):
    """parse table content into table-wrap tag"""
    table = OrderedDict()

    parts_match = re.match(r"(.*)(<table.*)", content)
    title_content = parts_match.group(1)
    table["table"] = parts_match.group(2)

    # check for table label only
    if re.match(r"^<bold>(.*)?<\/bold>", title_content):

        label_only_content_match = r"^<bold>(.*)?<\/bold>$"
        title_content_match = r"<bold>(.*)<\/bold>\&lt;.*?\&gt;(.*)?"

        if re.match(label_only_content_match, title_content):
            # simple bold label with no caption
            parts_match = re.match(label_only_content_match, title_content)
            table["label"] = parts_match.group(1)
        elif re.match(title_content_match, title_content):
            # strip &lt; open tag from the title_content
            parts_match = re.match(title_content_match, title_content)
            altered_title_content = "<bold>%s</bold>%s" % (
                parts_match.group(1),
                parts_match.group(2),
            )
            (
                table["label"],
                table["title"],
                table["content"],
            ) = extract_label_title_content(altered_title_content)
    else:
        bold_parts_match = r".*?<bold>(.*)?<\/bold>(.*)"
        if re.match(bold_parts_match, title_content):
            parts_match = re.match(bold_parts_match, title_content)
            altered_title_content = "<bold>%s</bold>%s" % (
                parts_match.group(1),
                parts_match.group(2),
            )
        else:
            altered_title_content = title_content
        (
            table["label"],
            table["title"],
            table["content"],
        ) = extract_label_title_content(altered_title_content)

    return table


def table_content(content):
    """convert and clean table XML"""
    # remove <col> tags
    content = re.sub(r"<col .*?\/>", "", content)
    # strip parent <table> tag
    return utils.clean_portion(content, "table")


def table_wrap_element(label, title, content, table):
    """populate a table-wrap element"""
    table_wrap_tag = Element("table-wrap")

    label_tag = SubElement(table_wrap_tag, "label")
    label_tag.text = label

    if title or content:
        caption_tag = SubElement(table_wrap_tag, "caption")
        if title:
            utils.append_to_parent_tag(
                caption_tag, "title", title, utils.XML_NAMESPACE_MAP
            )

        # append content as a p tag in the caption
        if content:
            utils.append_to_parent_tag(
                caption_tag, "p", content, utils.XML_NAMESPACE_MAP
            )

    if table:
        clean_table = table_content(table)
        utils.append_to_parent_tag(
            table_wrap_tag, "table", clean_table, utils.XML_NAMESPACE_MAP
        )
        # add attributes to the table tag
        table_tag = table_wrap_tag[-1]
        table_tag.set("frame", "hsides")
        table_tag.set("rules", "groups")

    return table_wrap_tag


def process_content_sections(content_sections, prefs=None):
    """profile each paragraph and add as an appropriate content block"""
    content_blocks = []
    appended_content = ""
    prev = {}
    # add a blank section for the final loop
    content_sections.append(OrderedDict())
    for section in content_sections:
        content_blocks, appended_content, prev = process_content_section(
            section, content_blocks, appended_content, prev, prefs
        )

    return content_blocks


def process_content_section(
    section, content_blocks, appended_content, prev, prefs=None
):
    """profile and format the section content adding content blocks"""
    tag_name = section.get("tag_name")
    content, tag_name, attr, action, wrap = process_content(
        tag_name, section.get("content"), prev, prefs
    )

    if (
        (prev.get("wrap") and not wrap)
        or (wrap and prev.get("wrap") and prev.get("wrap") != wrap)
        or (prev.get("wrap") and not content)
    ):
        content_blocks, appended_content, prev = finish_wrap(
            content_blocks, content, appended_content, prev
        )

    elif action == "add":
        if prev.get("action") == "append" and appended_content:
            content_blocks.append(
                ContentBlock(prev.get("tag_name"), appended_content, prev.get("attr"))
            )
            appended_content = ""
        if content and not wrap:
            content_blocks.append(ContentBlock(tag_name, content, attr))
            prev["content"] = None
            appended_content = ""
        elif content:
            appended_content = content
            prev["content"] = content

    elif action == "append":
        if appended_content:
            appended_content = appended_content + content
        else:
            appended_content = content
        prev["content"] = content

    prev["action"] = action
    prev["tag_name"] = tag_name
    prev["attr"] = attr
    prev["wrap"] = wrap

    return content_blocks, appended_content, prev


def finish_wrap(content_blocks, content, appended_content, prev):
    """add appended content to a wrap"""
    # finish the fig tag content
    if prev.get("wrap") == "fig":
        # format the content into the figure content block
        if content and match_fig_content_title_end(content):
            appended_content = appended_content + content

        # potentially multiple figs, parse and add to fig_content_list
        fig_content_list = []
        matches = re.finditer(FIG_CONTENT_START_PATTERN, appended_content)
        prev_start = None
        for match in matches:
            start = match.start()
            if prev_start is not None:
                fig_content_list.append(appended_content[prev_start:start])
            prev_start = start
        fig_content_list.append(appended_content[prev_start:])

        for fig_block_content in fig_content_list:
            fig_content = build_fig(fig_block_content)
            fig_tag = fig_element(
                fig_content.get("label"),
                fig_content.get("title"),
                fig_content.get("content"),
            )
            content_block_content = fig_element_to_string(fig_tag)
            content_blocks.append(
                ContentBlock("fig", content_block_content, prev.get("attr"))
            )
        prev["content"] = None
        if content and match_fig_content_title_end(content):
            appended_content = None
        else:
            appended_content = content
    elif prev.get("wrap") == "media":
        # format the content into the video media content block
        if content and match_video_content_title_end(content):
            appended_content = appended_content + content
        video_content = build_fig(appended_content)
        media_tag = media_element(
            video_content.get("label"),
            video_content.get("title"),
            video_content.get("content"),
        )
        content_block_content = media_element_to_string(media_tag)
        content_blocks.append(
            ContentBlock("media", content_block_content, media_tag.attrib)
        )
        prev["content"] = None
        if content and match_video_content_title_end(content):
            appended_content = None
        else:
            appended_content = content
    elif prev.get("wrap") == "disp-quote":
        disp_quote_tag = disp_quote_element(appended_content)
        content_block_content = disp_quote_element_to_string(disp_quote_tag)
        tag_attr = {"content-type": "editor-comment"}
        content_blocks.append(
            ContentBlock("disp-quote", content_block_content, tag_attr)
        )
        prev["content"] = content
        appended_content = content
    elif prev.get("wrap") == "table-wrap":
        if content and match_table_content_end(content):
            appended_content = appended_content + content
        table_content = build_table_wrap(appended_content)
        table_wrap_tag = table_wrap_element(
            table_content.get("label"),
            table_content.get("title"),
            table_content.get("content"),
            table_content.get("table"),
        )
        content_block_content = table_wrap_element_to_string(table_wrap_tag)
        content_blocks.append(
            ContentBlock("table-wrap", content_block_content, table_wrap_tag.attrib)
        )
        prev["content"] = None
        if content and match_table_content_end(content):
            appended_content = None

    return content_blocks, appended_content, prev


def process_content(tag_name, content, prev, prefs=None):
    if tag_name == "list":
        return process_list_content(content, prev)
    if tag_name == "table":
        return process_table_content(content)
    if tag_name == "p":
        return process_p_content(content, prev, prefs)
    if tag_name == "disp-quote":
        return process_disp_quote_content(content, prev)
    # default
    return content, None, None, "add", prev.get("wrap")


def process_table_content(content):
    """once a table tag is discovered close the wrapping element"""
    wrap = None
    return content, "table", None, "add", wrap


def process_list_content(content, prev=None):
    # simple replacement of list-type="order" with list-type="number"
    if not prev:
        prev = {}
    content = content.replace('<list list-type="order">', '<list list-type="number">')
    content = eautils.remove_tag("disp-quote", content)
    content_xml = ElementTree.fromstring(content)
    return (
        utils.clean_portion(content, "list"),
        "list",
        content_xml.attrib,
        "add",
        prev.get("wrap"),
    )


FIG_CONTENT_START_PATTERN = r"\&lt;[A-Za-z ]+ image [0-9]+?\.{0,1}\&gt;"


def match_fig_content_start(content):
    return bool(re.match(FIG_CONTENT_START_PATTERN, content))


def match_fig_content_title_start(content):
    return bool(re.match(r"^&lt;.*image [0-9]+? title\/legend\&gt;", content))


def match_fig_content_title_end(content):
    return bool(re.match(r".*\&lt;.*image [0-9]+? title\/legend\&gt;$", content))


def match_video_content_start(content):
    return bool(re.match(r"\&lt;.*video [0-9]+?\.{0,1}\&gt;", content))


def match_video_content_title_start(content):
    return bool(re.match(r"^&lt;.*video [0-9]+? title\/legend\&gt;", content))


def match_video_content_title_end(content):
    return bool(re.match(r".*\&lt;.*video [0-9]+? title\/legend\&gt;$", content))


def match_table_content_start(content):
    return bool(
        re.match(r"^<bold>.*[tT]able [0-9]+?.?<\/bold>$", content)
        or re.match(r"\&lt;[A-Za-z ]+ .*[tT]able [0-9]+?\&gt;", content)
    )


def match_table_content_end(content):
    return bool(re.match(r".*</table>$", content))


def match_disp_quote_content(content):
    return bool(re.match(r"^<italic>.*<\/italic>$", content))


def p_wrap(content):
    """wrap string in a <p> tag"""
    return "<p>%s</p>" % content


def clean_italic_p(content):
    """remove italic and wrap in p tag"""
    return p_wrap(eautils.remove_tag("italic", content))


def process_p_content(content, prev, prefs=None):
    """set paragraph content and decide to append or add to previous paragraph content"""
    action = "append"
    tag_name = "p"
    content = utils.clean_portion(content, "p")
    wrap = prev.get("wrap")

    # author response or decision letter image parsing
    if not wrap:
        if match_fig_content_start(content):
            wrap = "fig"
            action = "add"
        elif match_video_content_start(content):
            wrap = "media"
            action = "add"
        elif match_table_content_start(content):
            wrap = "table-wrap"
            action = "add"
        elif match_disp_quote_content(content):
            if prefs and prefs.get("italic_to_disp_quote"):
                wrap = "disp-quote"
                content = clean_italic_p(content)
                action = "add"

    if wrap and wrap != "disp-quote":
        if match_fig_content_title_end(content) or match_video_content_title_end(
            content
        ):
            action = "add"
            wrap = None
        elif (
            wrap == "fig"
            and prev.get("content")
            and match_fig_content_start(prev.get("content"))
            and not match_fig_content_title_start(content)
        ):
            if match_fig_content_start(content):
                # append content if two figs are listed in succession
                content = "%s%s" % (prev.get("content"), content)
                action = "add"
            else:
                # after a fig with no caption, check if the next paragraph
                # is another type of wrap or will be a disp-quote
                if not match_disp_quote_content(content):
                    if match_table_content_start(content):
                        wrap = "table-wrap"
                        action = "add"
                    elif match_video_content_start(content):
                        wrap = "media"
                        action = "add"
                    else:
                        wrap = None
                else:
                    wrap = "disp-quote"
                    content = clean_italic_p(content)
                    action = "add"
        elif (
            wrap == "media"
            and prev.get("content")
            and match_video_content_start(prev.get("content"))
            and not match_video_content_title_start(content)
        ):
            wrap = None
    elif wrap == "disp-quote":
        if match_table_content_start(content):
            wrap = "table-wrap"
        elif prev.get("wrap") == "disp-quote":
            if not match_disp_quote_content(content):
                wrap = None
            else:
                content = clean_italic_p(content)
    elif (
        not wrap
        and prev.get("content")
        and not prev.get("content").startswith("<disp-formula")
        and not content.startswith("<disp-formula")
    ):
        action = "add"

    return content, tag_name, None, action, wrap


def process_disp_quote_content(content, prev):
    return (
        utils.clean_portion(content, "disp-quote"),
        "disp-quote",
        None,
        "add",
        prev.get("wrap"),
    )
