import pytz

from datetime import date, timedelta

from django.conf import settings
from django.db import models
from django.test import TestCase
from edc_quota.client.models import QuotaMixin
from edc_quota.controller.models import Client, ControllerQuotaHistory, ControllerQuota
from edc_quota.controller.controller import Controller
from collections import defaultdict


tz = pytz.timezone(settings.TIME_ZONE)


class DummyController(Controller):

    def get_client_model_count(self, name):
        return 5

    def post_client_quota(self, name):
        pass


class TestQuotaModel2(QuotaMixin, models.Model):

    field1 = models.CharField(max_length=10)

    field2 = models.CharField(max_length=10)

    class Meta:
        app_label = 'edc_quota'


class TestController(TestCase):

    def setUp(self):

        self.quota = ControllerQuota.objects.create(
            app_label='edc_quota',
            model_name='TestQuotaModel2',
            target=3,
            start_date=date.today(),
            expiration_date=date.today() + timedelta(days=1)
        )

        for hostname in ['host{}'.format(n) for n in range(1, 10)]:
            Client.objects.create(
                hostname=hostname,
                app_label='edc_quota',
                model_name='TestQuotaModel2',
                is_active=True)

    def test_instantiate(self):
        controller = Controller(self.quota)
        self.assertEqual(controller.quota, self.quota)

    def test_register_clients(self):
        """Asserts controller only registers clients associated with its quota."""
        controller = Controller(self.quota)
        self.assertEqual(Client.objects.all().count(), len(controller.clients))
        Client.objects.create(
            hostname='hostname',
            app_label='edc_quota',
            model_name='TestQuotaModelNotMe',
            is_active=True)
        controller = Controller(self.quota)
        self.assertEqual(Client.objects.all().count() - 1, len(controller.clients))

    def test_clients_contacted(self):
        controller = DummyController(self.quota)
        controller.get_all()
        quota_history = ControllerQuotaHistory.objects.filter(quota=controller.quota).last()
        clients_contacted = quota_history.clients_contacted.split(',')
        clients_contacted.sort()
        self.assertEqual(clients_contacted, [c.name for c in Client.objects.all().order_by('hostname')])
        self.assertGreater(len(clients_contacted), 0)

    def test_quota_history(self):
        controller = DummyController(self.quota)
        controller.get_all()
        quota_history = ControllerQuotaHistory.objects.filter(quota=controller.quota).last()
        self.assertEqual(quota_history.model_count, 5 * len(quota_history.clients_contacted.split(',')))
        self.assertIsNotNone(quota_history.contacted)

    def test_post_all(self):
        controller = DummyController(self.quota)
        controller.get_all()
        controller.post_all()
        for client in Client.objects.all():
            self.assertEqual(client.contacted, controller.quota_history.contacted)
            self.assertEqual(client.target, 0)
            self.assertEqual(client.expiration_date, controller.quota_history.expiration_date)
        controller = DummyController(self.quota)
        controller.quota.target = 100
        controller.get_all()
        controller.post_all()
        for client in Client.objects.all():
            self.assertEqual(client.contacted, controller.quota_history.contacted)
            self.assertGreaterEqual(client.target, 5)
            self.assertEqual(client.expiration_date, controller.quota_history.expiration_date)

    def test_expired_quota(self):
        quota = ControllerQuota.objects.create(
            app_label='edc_quota',
            model_name='TestQuotaModel2',
            target=3,
            start_date=date.today() - timedelta(days=2),
            expiration_date=date.today() - timedelta(days=1)
        )
        with self.assertRaises(ControllerQuota.DoesNotExist):
            DummyController(quota)

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
