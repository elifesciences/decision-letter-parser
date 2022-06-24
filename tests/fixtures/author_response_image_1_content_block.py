# coding=utf-8
from elifearticle.article import ContentBlock

CONTENT = (
    "<label>Author response image 1.</label><caption><title>Title up to first full stop.</title>"
    r'<p>Caption <sup>2+</sup> calculated using<disp-formula><mml:math alttext="\alpha">'
    r'<mml:mi>α</mml:mi></mml:math></disp-formula><disp-formula><mml:math alttext="\beta">'
    "<mml:mi>β</mml:mi></mml:math></disp-formula>and those on the right panels using<disp-formula>"
    r'<mml:math alttext="\gamma"><mml:mi>γ</mml:mi></mml:math></disp-formula>under symmetrical'
    " ionic conditions. The number of barriers <inline-formula><mml:math "
    'display="inline" alttext="n"><mml:mi>n</mml:mi></mml:math></inline-formula> have their usual '
    'meanings.</p></caption><graphic mimetype="image" xlink:href="todo" />'
)

EXPECTED = ContentBlock("fig", CONTENT)
