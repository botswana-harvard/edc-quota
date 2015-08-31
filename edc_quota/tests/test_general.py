from django.test import TestCase

from edc_quota.override import Override, CodeError


class TestOverride(TestCase):

    def test_create_new_codes(self):
        override = Override()
        first_code = override.code
        self.assertIsNotNone(first_code)
        override = Override()
        second_code = override.code
        self.assertIsNotNone(second_code)
        self.assertNotEqual(first_code, second_code)

    def test_combination_invalid_without_confirmation(self):
        override = Override()
        self.assertFalse(override.is_valid_combination)

    def test_combination(self):
        override = Override()
        code = override.code
        self.assertFalse(override.is_valid_combination)
        override = Override(code)
        confirmation_code = override.confirmation_code
        self.assertFalse(override.is_valid_combination)
        override = Override(code, confirmation_code)
        self.assertTrue(override.is_valid_combination)

    def test_combination_blank(self):
        override = Override()
        override.code = ''
        self.assertRaises(CodeError, override.encode)

    def test_combination_has_valid_char(self):
        override = Override(code='624FZ')
        for c in override.confirmation_code:
            self.assertIn(c, override.allowed_chars)
        override.decode()
        for c in override.decoded:
            self.assertIn(c, override.allowed_chars)

#     def test_many_combinations(self):
#         n = 0
#         codes = []
#         print()
#         while n < 100000:
#             n += 1
#             override = Override()
#             code = override.code
#             confirmation_code = override.confirmation_code
#             override = Override(code, confirmation_code)
#             self.assertTrue(override.is_valid_combination)
#             self.assertNotIn(code, codes)
#             codes.append(code)
#             sys.stdout.write('{} \r'.format(n))
#             sys.stdout.flush()
