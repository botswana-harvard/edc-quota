import pytz

from datetime import datetime

from django.conf import settings
from django.db import models
from django.test import TestCase
from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase

from edc_quota_client.models import QuotaMixin, Quota
from edc_quota_client.exceptions import QuotaReachedError

tz = pytz.timezone(settings.TIME_ZONE)


class TestQuotaModel(QuotaMixin, models.Model):

    field1 = models.CharField(max_length=10)

    field2 = models.CharField(max_length=10)

    def save(self, *args, **kwargs):
        self.field2 = 'erik'
        super(TestQuotaModel, self).save(*args, **kwargs)

    class Meta:
        app_label = 'edc_quota_client'


class TestQuota(TestCase):

    def test_quota_model_create(self):
        expires = datetime.today()
        expires = datetime(expires.year, expires.month, expires.day, 23, 59)
        quota = Quota.objects.create(
            app_label='edc_quota_client', model_name='TestQuotaModel', target=2,
            expires_datetime=tz.localize(expires)
        )
        self.assertEqual(
            Quota.objects.filter(app_label='edc_quota_client', model_name='TestQuotaModel').last(), quota)
        self.assertEqual(
            Quota.objects.filter(
                app_label='edc_quota_client', model_name='TestQuotaModel',
                expires_datetime=tz.localize(expires)
            ).last(), quota)

    def test_quota_pk(self):
        """Assert test model picks the correct quota_pk on created and updated."""
        expires = datetime.today()
        expires = datetime(expires.year, expires.month, expires.day, 23, 59)
        quota1 = Quota.objects.create(
            app_label='edc_quota_client', model_name='TestQuotaModel', target=2,
            expires_datetime=tz.localize(expires)
        )
        test_model = TestQuotaModel()
        test_model.save()
        self.assertEqual(test_model.quota_pk, quota1.pk)
        expires = datetime(expires.year, expires.month, expires.day + 1, 23, 59)
        quota2 = Quota.objects.create(
            app_label='edc_quota_client', model_name='TestQuotaModel', target=2,
            expires_datetime=tz.localize(expires)
        )
        test_model.save()
        self.assertEqual(test_model.quota_pk, quota1.pk)
        test_model = TestQuotaModel()
        test_model.save()
        self.assertEqual(test_model.quota_pk, quota2.pk)

    def test_quota_model_count(self):
        """Asserts model_count is incremented on save / created."""
        expires = datetime.today()
        expires = datetime(expires.year, expires.month, expires.day, 23, 59)
        quota = Quota.objects.create(
            app_label='edc_quota_client', model_name='TestQuotaModel', target=2,
            expires_datetime=tz.localize(expires)
        )
        self.assertEqual(quota.model_count, 0)
        test_model = TestQuotaModel()
        test_model.save()
        quota = Quota.objects.get(pk=quota.pk)
        self.assertEqual(quota.model_count, 1)
        test_model.save()
        quota = Quota.objects.get(pk=quota.pk)
        self.assertEqual(quota.model_count, 1)
        test_model = TestQuotaModel()
        test_model.save()
        quota = Quota.objects.get(pk=quota.pk)
        self.assertEqual(quota.model_count, 2)

    def test_quota_reached(self):
        """Asserts mixin save method works with model save."""
        expires = datetime.today()
        expires = datetime(expires.year, expires.month, expires.day, 23, 59)
        quota = Quota.objects.create(
            app_label='edc_quota_client', model_name='TestQuotaModel',
            target=2,
            expires_datetime=tz.localize(expires)
        )
        test_model = TestQuotaModel()
        test_model.save()
        self.assertTrue(test_model.field2, 'erik')
        quota = Quota.objects.get(pk=quota.pk)
        self.assertEqual(quota.model_count, 1)
        test_model = TestQuotaModel()
        test_model.save()
        quota = Quota.objects.get(pk=quota.pk)
        self.assertEqual(quota.model_count, 2)
        self.assertRaises(QuotaReachedError, TestQuotaModel.objects.create)
        self.assertEqual(TestQuotaModel.objects.all().count(), 2)

    def test_change_quota(self):
        """Asserts quota is reached and then can be changed on the class."""
        expires = datetime.today()
        expires = datetime(expires.year, expires.month, expires.day, 23, 59)
        quota = Quota.objects.create(
            app_label='edc_quota_client', model_name='TestQuotaModel',
            target=2,
            expires_datetime=tz.localize(expires)
        )
        TestQuotaModel.objects.create()
        TestQuotaModel.objects.create()
        self.assertRaises(QuotaReachedError, TestQuotaModel.objects.create)
        quota.target = 1
        quota.save()
        self.assertRaises(QuotaReachedError, TestQuotaModel.objects.create)
        quota.target = 3
        quota.save()
        self.assertIsInstance(TestQuotaModel.objects.create(), TestQuotaModel)
