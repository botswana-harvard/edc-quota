from getresults_identifier import ShortIdentifier


class OverrideError(Exception):
    pass


class CodeError(Exception):
    pass


class Override(object):
    """
    Get an override code:
        >>> from edc_quota import Override
        >>> override = Override()
        >>> code = override.code
        >>> print(code)
        '3UFY9'

    Ask for a confirmation code
        >>> from edc_quota import Override
        >>> override = Override(code)
        >>> confirmation_code = override.confirmation_code
        >>> print(confirmation_code)
        'NC4GT'

    Validate the pair of codes
        >>> from edc_quota import Override
        >>> if Override('3UFY9', 'NC4GT').is_valid_combination:
        >>>>    print('the codes are a valid pair')

    """

    identifier_type = 'override'
    prefix_pattern = ''

    def __init__(self, code=None, confirmation_code=None):
        self._code = None
        self.encoded = ''
        self.decoded = ''
        ShortIdentifier.prefix_pattern = ''
        self.allowed_chars = ShortIdentifier.allowed_chars
        self.code = code or ShortIdentifier().identifier
        if confirmation_code:
            self.encoded = confirmation_code
            self.decode()
        else:
            self.encode()

    def __repr__(self):
        return '{}(\'{}\')'.format(self.__class__.__name__, self.code)

    def __str__(self):
        return '{}'.format(self.code)

    @property
    def confirmation_code(self):
        return self.encoded

    @property
    def is_valid_combination(self):
        return self.code == self.decoded

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        self._code = value
        self.encoded = ''

    def encode(self):
        """Encodes the 'code' instance attribute which is a short alphanumeric."""
        if not self.encoded:
            for c in self.code:
                encoded_c = None
                while True:
                    encoded_c = chr((ord(encoded_c or c) + len(self.allowed_chars)) % 126)
                    if encoded_c in self.allowed_chars:
                        break
                self.encoded += encoded_c
            if not self.encoded:
                raise CodeError('Unable to encode \'{}\'.'.format(self.code))

    def decode(self):
        """Decodes the 'encoded' attribute and returns a short alphanumeric encoded by this class."""
        if self.encoded:
            for c in self.encoded:
                decoded_c = None
                while True:
                    decoded_c = chr((ord(decoded_c or c) - len(self.allowed_chars)) % 126)
                    if decoded_c in self.allowed_chars:
                        break
                self.decoded += decoded_c
