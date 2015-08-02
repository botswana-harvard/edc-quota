import pytz

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase
from tastypie.utils import make_naive
from edc_quota_client.models import QuotaMixin
from edc_quota_controller.models import Client, QuotaHistory, Quota
from edc_quota_controller.controller import Controller

tz = pytz.timezone(settings.TIME_ZONE)


class TestQuotaModel(QuotaMixin, models.Model):

    field1 = models.CharField(max_length=10)

    field2 = models.CharField(max_length=10)

    class Meta:
        app_label = 'edc_quota_controller'


class TestController(TestCase):

    def setUp(self):

        self.quota = Quota.objects.create(
            app_label='edc_quota_controller',
            model_name='TestQuotaModel',
            target=3,
            expires_datetime=timezone.now() + timedelta(days=1)
        )

        for hostname in ['host{}'.format(n) for n in range(1, 10)]:
            Client.objects.create(
                hostname=hostname,
                app_label='edc_quota_controller',
                model_name='TestQuotaModel',
                is_active=True)

    def test_instantiate(self):
        controller = Controller(self.quota)
        self.assertEqual(controller.quota, self.quota)
        controller = Controller(
            app_label='edc_quota_controller',
            model_name='TestQuotaModel',
        )
        self.assertEqual(controller.quota, self.quota)

    def test_register_clients(self):
        """Asserts controller only registers clients associated with its quota."""
        controller = Controller(self.quota)
        self.assertEqual(Client.objects.all().count(), len(controller.clients))
        Client.objects.create(
            hostname='hostname',
            app_label='edc_quota_controller',
            model_name='TestQuotaModelNotMe',
            is_active=True)
        controller = Controller(self.quota)
        self.assertEqual(Client.objects.all().count() - 1, len(controller.clients))
