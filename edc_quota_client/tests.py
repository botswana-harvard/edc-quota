import pytz

from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.test import TestCase
from django.utils import timezone
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
        quota = Quota.objects.create(
            app_label='edc_quota_client',
            model_name='TestQuotaModel',
            target=2,
            expires_datetime=timezone.now() + timedelta(days=1)
        )
        self.assertEqual(
            Quota.objects.filter(
                app_label='edc_quota_client',
                model_name='TestQuotaModel').last(), quota)
        self.assertEqual(
            Quota.objects.filter(
                app_label='edc_quota_client',
                model_name='TestQuotaModel',
            ).last(), quota)

    def test_quota_pk(self):
        """Assert test model picks the correct quota_pk on created and updated."""
        quota1 = Quota.objects.create(
            app_label='edc_quota_client',
            model_name='TestQuotaModel',
            target=2,
            expires_datetime=timezone.now() + timedelta(days=1)
        )
        test_model = TestQuotaModel()
        test_model.save()
        self.assertEqual(test_model.quota_pk, quota1.pk)
        quota2 = Quota.objects.create(
            app_label='edc_quota_client',
            model_name='TestQuotaModel',
            target=2,
            expires_datetime=timezone.now() + timedelta(days=1)
        )
        test_model.save()
        self.assertEqual(test_model.quota_pk, quota1.pk)
        test_model = TestQuotaModel()
        test_model.save()
        self.assertEqual(test_model.quota_pk, quota2.pk)

    def test_quota_model_count_with_save(self):
        """Asserts model_count is incremented on save / created."""
        quota = Quota.objects.create(
            app_label='edc_quota_client',
            model_name='TestQuotaModel',
            target=2,
            expires_datetime=timezone.now() + timedelta(days=1)
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

    def test_quota_model_count_with_create(self):
        """Asserts model_count is incremented on save / created."""
        quota = Quota.objects.create(
            app_label='edc_quota_client',
            model_name='TestQuotaModel',
            target=2,
            expires_datetime=timezone.now() + timedelta(days=1)
        )
        self.assertEqual(quota.model_count, 0)
        test_model = TestQuotaModel.objects.create()
        quota = Quota.objects.get(pk=quota.pk)
        self.assertEqual(quota.model_count, 1)
        test_model.save()
        quota = Quota.objects.get(pk=quota.pk)
        self.assertEqual(quota.model_count, 1)
        test_model = TestQuotaModel.objects.create()
        quota = Quota.objects.get(pk=quota.pk)
        self.assertEqual(quota.model_count, 2)

    def test_quota_reached(self):
        """Asserts mixin save method works with model save."""
        quota = Quota.objects.create(
            app_label='edc_quota_client',
            model_name='TestQuotaModel',
            target=2,
            expires_datetime=timezone.now() + timedelta(days=1)
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

    def test_increase_quota(self):
        """Asserts quota is reached and then can be changed on the class."""
        quota = Quota.objects.create(
            app_label='edc_quota_client', model_name='TestQuotaModel',
            target=2,
            expires_datetime=timezone.now() + timedelta(days=1)
        )
        TestQuotaModel.objects.create()
        TestQuotaModel.objects.create()
        self.assertRaises(QuotaReachedError, TestQuotaModel.objects.create)
        quota.target = 3
        quota.save()
        self.assertIsInstance(TestQuotaModel.objects.create(), TestQuotaModel)

    def test_decrease_quota(self):
        """Asserts quota is reached and then can be changed on the class."""
        Quota.objects.create(
            app_label='edc_quota_client',
            model_name='TestQuotaModel',
            target=2,
            expires_datetime=timezone.now() + timedelta(days=1)
        )
        TestQuotaModel.objects.create()
        TestQuotaModel.objects.create()
        self.assertRaises(QuotaReachedError, TestQuotaModel.objects.create)
        quota = Quota.objects.last()
        quota.target = 1
        quota.save()
        quota = Quota.objects.last()
        self.assertRaises(QuotaReachedError, TestQuotaModel.objects.create)

    def test_expired_quota(self):
        """Asserts quota is reached if expired."""
        Quota.objects.create(
            app_label='edc_quota_client', model_name='TestQuotaModel',
            target=2,
            expires_datetime=timezone.now() + timedelta(days=-1)
        )
        self.assertRaises(QuotaReachedError, TestQuotaModel.objects.create)

    def test_large_quota(self):
        Quota.objects.create(
            app_label=TestQuotaModel._meta.app_label,
            model_name=TestQuotaModel._meta.object_name,
            expires_datetime=timezone.now() + timedelta(days=1),
            target=100
        )
        for _ in range(0, 100):
            TestQuotaModel.objects.create()
        self.assertRaises(QuotaReachedError, TestQuotaModel.objects.create)
        quota = Quota.objects.last()
        self.assertEqual(quota.model_count, 100)
