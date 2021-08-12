from collections import OrderedDict


EXPECTED = [
    OrderedDict([
        ('section_type', 'preamble'),
        ('content', '<p><bold>Preamble</bold></p><p>Preamble ....</p>')
    ]),
    OrderedDict([
        ('section_type', 'decision_letter'),
        ('content', '<p><bold>Decision letter</bold></p><p>Decision letter ....</p>')
    ]),
    OrderedDict([
        ('section_type', 'author_response'),
        ('content', '<p><bold>Author response</bold></p><p>Author response ....</p>')
    ])
]
