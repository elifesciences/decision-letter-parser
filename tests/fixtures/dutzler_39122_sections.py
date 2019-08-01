# coding=utf-8

from tests import read_fixture

EXPECTED = [
    {None: ''},
    {'decision_letter': read_fixture('dutzler_39122_section_2.txt')},
    {'author_response': read_fixture('dutzler_39122_section_3.txt')}
]
