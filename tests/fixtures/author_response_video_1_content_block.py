# coding=utf-8
from letterparser.objects import ContentBlock


CONTENT = (
    '<label>Author response video 1.</label><caption><title>Title up to first full stop.</title>'
    '<p>Caption <sup>2+</sup>.</p></caption>')


ATTR = {
    'mimetype': 'video',
    'xlink:href': 'todo'
}


EXPECTED = ContentBlock('media', CONTENT, ATTR)
