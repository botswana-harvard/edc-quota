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
from collections import defaultdict

tz = pytz.timezone(settings.TIME_ZONE)


class DummyController(Controller):

    def get_client_model_count(self, name):
        return 5

    def put_client_quota(self, name):
        pass


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

    def test_clients_contacted(self):
        controller = DummyController(self.quota)
        controller.get_all()
        quota_history = QuotaHistory.objects.filter(quota=controller.quota).last()
        clients_contacted = quota_history.clients_contacted.split(',')
        clients_contacted.sort()
        self.assertEqual(clients_contacted, [c.name for c in Client.objects.all().order_by('hostname')])
        self.assertGreater(len(clients_contacted), 0)

    def test_quota_history(self):
        controller = DummyController(self.quota)
        controller.get_all()
        quota_history = QuotaHistory.objects.filter(quota=controller.quota).last()
        self.assertEqual(quota_history.model_count, 5 * len(quota_history.clients_contacted.split(',')))
        self.assertIsNotNone(quota_history.last_contact)

    def test_put_all(self):
        controller = DummyController(self.quota)
        controller.get_all()
        controller.put_all()
        for client in Client.objects.all():
            self.assertEqual(client.last_contact, controller.quota_history.last_contact)
            self.assertEqual(client.target, 0)
            self.assertEqual(client.expires_datetime, controller.quota_history.expires_datetime)
        controller = DummyController(self.quota)
        controller.quota.target = 100
        controller.get_all()
        controller.put_all()
        for client in Client.objects.all():
            self.assertEqual(client.last_contact, controller.quota_history.last_contact)
            self.assertGreaterEqual(client.target, 5)
            self.assertEqual(client.expires_datetime, controller.quota_history.expires_datetime)

    def test_target1(self):
        clients = defaultdict(int)
        controller = DummyController(self.quota)
        controller.quota.target = 95
        controller.quota.model_count = 50
        allocation = controller.quota.target - controller.quota.model_count
        client_count = 6
        remainder = allocation % client_count if allocation > 0 else 0
        for name in ['a', 'b', 'c', 'd', 'e', 'f']:
            target, remainder = controller.target(allocation, client_count, remainder)
            clients[name] = target
        self.assertEqual(sum(clients.values()), allocation)

    def test_target2(self):
        clients = defaultdict(int)
        controller = DummyController(self.quota)
        controller.quota.target = 95
        controller.quota.model_count = 37
        allocation = controller.quota.target - controller.quota.model_count
        client_count = 7
        remainder = allocation % client_count if allocation > 0 else 0
        for name in ['a', 'b', 'c', 'd', 'e', 'f', 'g']:
            target, remainder = controller.target(allocation, client_count, remainder)
            clients[name] = target
        self.assertEqual(sum(clients.values()), allocation)

    def test_target_if_negative(self):
        clients = defaultdict(int)
        controller = DummyController(self.quota)
        controller.quota.target = 95
        controller.quota.model_count = 100
        allocation = controller.quota.target - controller.quota.model_count
        client_count = 6
        remainder = allocation % client_count if allocation > 0 else 0
        for name in ['a', 'b', 'c', 'd', 'e', 'f']:
            target, remainder = controller.target(allocation, client_count, remainder)
            clients[name] = target
        self.assertEqual(sum(clients.values()), 0)

    def test_set_new_target(self):
        controller = DummyController(self.quota)
        controller.quota.target = 100
        controller.get_all()
        allocation = controller.quota.target - controller.quota_history.model_count
        sum([client.target for client in controller.clients.values()])
        self.assertEqual(sum([client.target for client in controller.clients.values()]), allocation)
