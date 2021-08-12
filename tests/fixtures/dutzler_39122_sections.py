# coding=utf-8
from collections import OrderedDict
from tests import read_fixture

EXPECTED = [
    OrderedDict(
        [
            ("section_type", "decision_letter"),
            ("content", read_fixture("dutzler_39122_section_1.txt")),
        ]
    ),
    OrderedDict(
        [
            ("section_type", "author_response"),
            ("content", read_fixture("dutzler_39122_section_2.txt")),
        ]
    ),
]
