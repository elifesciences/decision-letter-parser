# coding=utf-8
from collections import OrderedDict


EXPECTED = [
    OrderedDict(
        [("tag_name", "p"), ("content", "<p>&lt;Author response image 1&gt;</p>")]
    ),
    OrderedDict(
        [
            ("tag_name", "p"),
            (
                "content",
                (
                    "<p>&lt;Author response image 1 title/legend&gt;<bold>Author response image 1.</bold>"
                    " Title up to first full stop. Caption <sup>2+</sup> calculated using</p>"
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
                    '<p xmlns:mml="http://www.w3.org/1998/Math/MathML"><disp-formula>'
                    '<mml:math alttext="\\alpha"><mml:mi>α</mml:mi></mml:math></disp-formula></p>'
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
                    '<p xmlns:mml="http://www.w3.org/1998/Math/MathML"><disp-formula>'
                    '<mml:math alttext="\\beta"><mml:mi>β</mml:mi></mml:math></disp-formula></p>'
                ),
            ),
        ]
    ),
    OrderedDict(
        [("tag_name", "p"), ("content", "<p>and those on the right panels using</p>")]
    ),
    OrderedDict(
        [
            ("tag_name", "p"),
            (
                "content",
                (
                    '<p xmlns:mml="http://www.w3.org/1998/Math/MathML"><disp-formula>'
                    '<mml:math alttext="\\gamma"><mml:mi>γ</mml:mi></mml:math></disp-formula></p>'
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
                    '<p xmlns:mml="http://www.w3.org/1998/Math/MathML">under symmetrical ionic conditions.'
                    ' The number of barriers <inline-formula><mml:math alttext="n" display="inline">'
                    "<mml:mi>n</mml:mi></mml:math></inline-formula> have their usual meanings."
                    "&lt;/Author response image 1 title/legend&gt;</p>"
                ),
            ),
        ]
    ),
]
