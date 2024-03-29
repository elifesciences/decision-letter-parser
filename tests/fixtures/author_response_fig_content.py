# coding=utf-8
from collections import OrderedDict


EXPECTED = OrderedDict(
    [
        ("label", "Author response image 1."),
        ("title", "Title up to first full stop."),
        (
            "content",
            (
                "Caption <sup>2+</sup> calculated using</p><p><disp-formula><alternatives>"
                "<tex-math><![CDATA[\\alpha]]></tex-math><mml:math><mml:mi>α</mml:mi></mml:math>"
                "</alternatives></disp-formula></p><p><disp-formula><alternatives><tex-math>"
                "<![CDATA[\\beta]]></tex-math><mml:math><mml:mi>β</mml:mi></mml:math></alternatives>"
                "</disp-formula></p><p>and those on the right panels using</p><p><disp-formula>"
                "<alternatives><tex-math><![CDATA[\\gamma]]></tex-math><mml:math><mml:mi>γ</mml:mi>"
                "</mml:math></alternatives></disp-formula></p><p>under symmetrical ionic conditions."
                " The number of barriers <inline-formula><alternatives><tex-math><![CDATA[n]]>"
                '</tex-math><mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" display="inline">'
                "<mml:mi>n</mml:mi></mml:math></alternatives></inline-formula>"
                " have their usual meanings."
            ),
        ),
    ]
)
