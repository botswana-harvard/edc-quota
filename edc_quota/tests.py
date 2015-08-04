from django.test import TestCase

from .override import Override, CodeError


class TestOverride(TestCase):

    def test_create_code(self):
        first_code = Override().code
        self.assertIsNotNone(first_code)
        second_code = Override().code
        self.assertIsNotNone(second_code)
        self.assertNotEqual(first_code, second_code)

    def test_combination(self):
        override = Override()
        self.assertFalse(override.validate_combination())
        code, confirmation_code = override.make_confirmation_code()
        self.assertIsNotNone(confirmation_code)
        self.assertTrue(override.validate_combination(code, confirmation_code))

    def test_combination_code_returns_code(self):
        override = Override()
        code1 = override.code
        code2, _ = override.make_confirmation_code(code1)
        self.assertEqual(code1, code2)

    def test_combination_manually(self):
        override = Override()
        code1 = override.code
        _, confirmation_code = override.make_confirmation_code(code1)
        self.assertTrue(override.validate_combination(code1, confirmation_code))

    def test_combination_blank(self):
        override = Override()
        override.code = ''
        self.assertRaises(CodeError, override.make_confirmation_code, '')
