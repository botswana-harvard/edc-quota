from getresults_identifier import ShortIdentifier


class OverrideError(Exception):
    pass


class CodeError(Exception):
    pass


class Override(object):
    """
    Get an override code:
        >>> from edc_quota import Override
        >>> override_code = Override().code

    Ask for a confirmation code
        >>> from edc_quota import Override
        >>> override_code = Override(code).confirmation_code

    Validate the pair of codes
        >>> from edc_quota import Override
        >>> if Override('3UFY9', confirmation_code).is_valid_combination:
        >>>>    print('Thanks, I win!')
    """

    identifier_type = 'override'
    prefix_pattern = ''

    def __init__(self, code=None, confirmation_code=None):
        ShortIdentifier.prefix_pattern = ''
        self.allowed_chars = ShortIdentifier.allowed_chars
        code = code or ShortIdentifier().identifier
        self.code, self.confirmation_code = confirmation_code or self.make_confirmation_code(code)
        self.is_valid_combination = self.validate_combination()

    def make_confirmation_code(self, code=None):
        """Returns a tuple of code, confirmation code where the confirmation code
        is based on the code (override code)."""
        self.confirmation_code = None
        code = code or self.code
        return code, self.make_code(code)

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
        original_code = self.unmake_code(confirmation_code)
        is_valid = original_code == code
        if not is_valid:
            self.error_message = (
                'Overide and confirmation codes do not match as a pair. Got {} and {}').format(
                    code, confirmation_code)
        return is_valid

    def make_code(self, code):
        new_code = ''
        for x in code:
            if x not in self.allowed_chars:
                raise CodeError(
                    'Unable to make a code from \'{}\'. '
                    'Got invalid character {}'.format(code, x)
                )
            p = (ord(x) + len(code)) % 126
            if p < 32:
                p = p + 31
            new_code += chr(p)
        if not new_code:
            raise CodeError('Unable to make a code from \'{}\'.'.format(code))
        return new_code

    def unmake_code(self, code):
        original_code = ''
        for x in code:
            if x not in self.allowed_chars:
                raise CodeError(
                    'Unable to determine the original code from \'{}\'. '
                    'Got invalid character {}'.format(code, x)
                )
            p = (ord(x) - len(code)) % 126
            if p < 32:
                p = p + 95
            original_code += chr(p)
        if not original_code:
            raise CodeError('Unable to determine the original code from \'{}\'.'.format(code))
        return original_code
