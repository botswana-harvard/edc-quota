from django.db import models
from django.test import TestCase
from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase

from edc_quota.quota_mixin import QuotaMixin
from edc_quota.exceptions import QuotaReachedError
from edc_quota.models import ClientQuota


class TestQuotaModel(QuotaMixin, models.Model):

    field1 = models.CharField(max_length=10)

    field2 = models.CharField(max_length=10)

    def save(self, *args, **kwargs):
        self.field2 = 'erik'
        super(TestQuotaModel, self).save(*args, **kwargs)

    class Meta:
        app_label = 'edc_quota'


class TestQuota(TestCase):

    def test_mixin_save(self):
        """Asserts mixin save method works with model save."""
        TestQuotaModel.quota = 2
        test_model = TestQuotaModel()
        test_model.save()
        self.assertTrue(test_model.field2, 'erik')
        TestQuotaModel.objects.create()
        self.assertRaises(QuotaReachedError, TestQuotaModel.objects.create)

    def test_mixin_quota_with_model_class(self):
        """Asserts quota is reached and then can be changed on the class."""
        TestQuotaModel.quota = 2
        TestQuotaModel.objects.create()
        TestQuotaModel.objects.create()
        self.assertRaises(QuotaReachedError, TestQuotaModel.objects.create)
        TestQuotaModel.quota = 3
        self.assertIsInstance(TestQuotaModel.objects.create(), TestQuotaModel)
