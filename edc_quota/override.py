from getresults_identifier import ShortIdentifier


class OverrideError(Exception):
    pass


class Override(object):

    identifier_type = 'override'
    prefix_pattern = ''

    def __init__(self, code=None, confirmation_code=None):
        ShortIdentifier.prefix_pattern = ''
        self.allowed_chars = ShortIdentifier.allowed_chars
        self.code = code or ShortIdentifier().identifier
        self.confirmation_code = confirmation_code
        self.validate_combination()

    def create_confirmation_code(self, code=None):
        """Generate a second key using the ASCII code from the first key characters"""
        code = code or self.code
        confirmation_code = ''
        if self.code:
            for x in self.code:
                if x in self.allowed_chars:
                    p = (ord(x) + len(self.code)) % 126
                    if p < 32:
                        p = p + 31
                    confirmation_code += chr(p)
        return self.code, confirmation_code or None

    def validate_combination(self, code=None, confirmation_code=None):
        """Reverse the second key and compare it to the first key"""
        self.error_message = None
        code = code or self.code
        confirmation_code = confirmation_code or self.confirmation_code
        if not code:
            self.error_message = 'No override code supplied'
            return False
        if not confirmation_code:
            self.error_message = 'No confirmation code supplied for {}'.format(self.code)
            return False
        validated_code = ''
        for x in confirmation_code:
            p = (ord(x) - len(confirmation_code)) % 126
            if p < 32:
                p = p + 95
            validated_code += chr(p)
        is_valid = validated_code == code
        if not is_valid:
            self.error_message = (
                'Overide and confirmation codes are not pair. Got {} and {}').format(
                    self.code, self.confirmation_code)
        return is_valid
