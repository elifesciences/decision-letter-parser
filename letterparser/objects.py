from elifetools import utils as etoolsutils


class ContentBlock(object):
    def __new__(cls, block_type=None, content=None):
        new_instance = object.__new__(cls)
        new_instance.init(block_type, content)
        return new_instance

    def init(self, block_type=None, content=None):
        self.block_type = block_type
        self.content = content
        self.content_blocks = []
        self.attr = {}

    def attr_names(self):
        """list of tag attribute names"""
        if self.attr:
            return list(self.attr.keys())
        return []

    def attr_string(self):
        """tag attributes formatted as a string"""
        string = ''
        if self.attr:
            for key, value in sorted(self.attr.items()):
                attr = '%s="%s"' % (
                    key, etoolsutils.escape_ampersand(value).replace('"', '&quot;'))
                string = ' '.join([string, attr])
        return string
