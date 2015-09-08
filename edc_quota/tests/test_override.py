from datetime import timedelta, date
from django.test import TestCase

from edc_quota.client.models import Quota
# from edc_quota.models import Override as OverrideModel
from edc_quota.override import SimpleOverride, Override, CodeError, Code

from .test_client import TestQuotaModel
from edc_quota.client.exceptions import QuotaReachedError
from edc_quota.override.models import OverrideModel


class TestOverride(TestCase):

    def test_code_accepts_code(self):
        code = Code()
        string_code = str(code)
        code1 = Code(code)
        code2 = Code(string_code)
        self.assertEqual(code1.plain_code, code2.plain_code)
        self.assertIsNotNone(string_code)

    def test_comparison(self):
        code1 = Code()
        str1 = str(code1)
        code2 = Code(code1)
        str2 = str(code2)
        self.assertEqual(code1, code2)
        self.assertFalse(code1 is code2)
        self.assertEqual(str1, str2)

    def test_code_not_validated(self):
        code = Code('AAAAA')
        self.assertFalse(code.validate(None))

    def test_code_validated(self):
        code = Code()
        plain_code = str(code)
        validation_code = code.validation_code
        code = Code(plain_code)
        self.assertTrue(code.validate(validation_code))

    def test_create_new_codes(self):
        override = SimpleOverride()
        first_code = override.request_code
        self.assertIsNotNone(first_code)
        override = SimpleOverride()
        second_code = override.request_code
        self.assertIsNotNone(second_code)
        self.assertNotEqual(first_code, second_code)

    def test_combination_invalid_without_confirmation(self):
        override = SimpleOverride()
        self.assertFalse(override.is_valid_combination)
        override = SimpleOverride(request_code='AAAAA')
        self.assertFalse(override.is_valid_combination)

    def test_cannot_validate(self):
        override = SimpleOverride()
        request_code = override.request_code
        self.assertFalse(override.is_valid_combination)
        override = SimpleOverride(request_code=request_code)
        self.assertIsNotNone(override.override_code)
        self.assertFalse(override.is_valid_combination)

    def test_combination_blank(self):
        override = SimpleOverride(request_code='', override_code='')
        self.assertFalse(override.is_valid_combination)

    def test_combination_has_valid_char(self):
        code = Code()
        allowed_chars = code.allowed_chars
        override_code = SimpleOverride(request_code='624FZ').override_code
        self.assertIsNotNone(override_code)
        for c in override_code:
            self.assertIn(c, allowed_chars)
        for c in code.decode(override_code):
            self.assertIn(c, allowed_chars)

    def test_override_init_with_none(self):
        override = Override()
        self.assertIsNotNone(override.request_code)
        self.assertIsNotNone(override.override_code)
        self.assertFalse(override.may_validate)

    def test_override_with_request(self):
        override = Override()
        request_code = override.request_code
        override = Override(request_code=request_code, override_code='AAAAA')
        self.assertIsNotNone(override.request_code)
        self.assertIsNotNone(override.override_code)
        self.assertFalse(override.is_valid_combination)

    def test_override_in_model(self):
        TestQuotaModel.objects.set_quota(2, date.today())
        TestQuotaModel.objects.create()
        TestQuotaModel.objects.create()
        self.assertRaises(QuotaReachedError, TestQuotaModel.objects.create)
        test_quota_model = TestQuotaModel()
        request_code = Code()
        test_quota_model.request_code = request_code
        code = Code(test_quota_model.request_code)
        test_quota_model.override(code.validation_code)
        test_quota_model.save()

#     def test_override_quota(self):
#         quota = Quota.objects.create(
#             app_label='edc_quota',
#             model_name='TestQuotaModel',
#             target=2,
#             expiration_date=date.today() + timedelta(days=1)
#         )
#         TestQuotaModel.objects.create()
#         TestQuotaModel.objects.create()
#         self.assertRaises(QuotaReachedError, TestQuotaModel.objects.create)
#         override = Override()
#         request_code = override.request_code
#         override = Override(request_code=request_code)
#         override_code = override.override_code
#         self.assertIsInstance(TestQuotaOverrideModel.objects.create(
#             request_code=code,
#             override_code=override_code,
#             quota=quota), QuotaOverride)
# 
#     def test_override_used(self):
#         """Assert fail on reusing the same code pair"""
#         quota = Quota.objects.create(
#             app_label='edc_quota',
#             model_name='TestQuotaOverrideModel',
#             target=1,
#             expiration_date=date.today() + timedelta(days=1)
#         )
#         TestQuotaOverrideModel.objects.create(quota=quota)
#         override = Override()
#         request_code = override.code
#         override = Override(request_code)
#         override_code = override.override_code
#         test_quota = TestQuotaOverrideModel.objects.create(
#             quota=quota,
#             request_code=request_code,
#             override_code=override_code,
#         )
#         with self.assertRaises(OverrideError):
#             TestQuotaOverrideModel.objects.create(
#                 request_code=test_quota.request_code,
#                 override_code=test_quota.override_code,
#                 quota=quota,
#             )
