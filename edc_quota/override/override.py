from getresults_identifier import ShortIdentifier
from edc_quota.override.models import OverrideModel
from django.db import IntegrityError, transaction


class OverrideError(Exception):
    pass


class CodeError(Exception):
    pass

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


class SimpleOverride(object):
    """
    Get an request code:
        >>> from edc_quota import Override
        >>> override = Override()
        >>> request_code = override.request_code
        >>> print(request_code)
        '3UFY9'

    Ask for a confirmation code
        >>> from edc_quota import Override
        >>> override = Override(request_code='3UFY9')
        >>> override_code = override.override_code
        >>> print(override_code)
        'NC4GT'

    Validate the pair of codes
        >>> from edc_quota import Override
        >>> if Override('3UFY9', 'NC4GT').is_valid_combination:
        >>>>    print('the codes are a valid pair')

    """

    identifier_type = 'override'
    prefix_pattern = ''

    def __init__(self, request_code=None, override_code=None):
        self.may_validate = False
        if request_code:
            self.request_code = Code(request_code)
            if override_code:
                self.may_validate = True
            self.override_code = override_code or self.request_code.validation_code
        else:
            self.request_code = Code()
            self.override_code = self.request_code.validation_code

    def __repr__(self):
        return '{}(\'{}\')'.format(self.__class__.__name__, str(self.request_code))

    @property
    def is_valid_combination(self):
        if self.may_validate:
            return self.request_code.validate(self.override_code)
        else:
            return False


class Override(SimpleOverride):

    def __init__(self, instance=None, request_code=None, override_code=None):
        super(Override, self).__init__(request_code, override_code)
        self.override_model = None
        if self.is_valid_combination and self.may_validate:
            if self.request_code and self.override_code and instance:
                with transaction.atomic():
                    try:
                        self.override_model = OverrideModel.objects.get(
                            request_code=request_code, pk__isnull=True)
                    except OverrideModel.DoesNotExist:
                        try:
                            self.override_model = OverrideModel.objects.create(
                                request_code=request_code, override_code=override_code,
                                app_label=instance._meta.app_label, model_name=instance._meta.model_name)
                        except IntegrityError:
                            pass
                if self.is_valid_combination and instance:
                    self.override_model.instance_pk = instance.pk
