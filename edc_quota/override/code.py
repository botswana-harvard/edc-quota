from getresults_identifier import ShortIdentifier

from .exceptions import CodeError

ShortIdentifier.prefix_pattern = ''


class Code(object):

    allowed_chars = ShortIdentifier.allowed_chars

    def __init__(self, code=None):
        if code:
            code = str(code)
        self.plain_code = code or ShortIdentifier().identifier

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.plain_code)

    def __str__(self):
        return self.plain_code

    def __eq__(self, other):
        return self.plain_code == other

    def __ne__(self, other):
        return self.plain_code != other

    def validate(self, code, decode=None):
        decode = True if decode is None else decode
        try:
            if decode:
                code = self.decode(code)
            return code == self.plain_code
        except CodeError:
            return False

    @property
    def validation_code(self):
        return self.encode(self.plain_code)

    def encode(self, code):
        if code:
            new_code = ''
            for c in code:
                encoded_c = None
                while True:
                    encoded_c = chr((ord(encoded_c or c) + len(self.allowed_chars)) % 126)
                    if encoded_c in self.allowed_chars:
                        break
                new_code += encoded_c
            if not code:
                raise CodeError('Unable to encode \'{}\'.'.format(code))
            return new_code
        return code

    def decode(self, code):
        if code:
            new_code = ''
            for c in code:
                decoded_c = None
                while True:
                    decoded_c = chr((ord(decoded_c or c) - len(self.allowed_chars)) % 126)
                    if decoded_c in self.allowed_chars:
                        break
                new_code += decoded_c
            return new_code
        return code
