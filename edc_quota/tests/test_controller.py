import pytz

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase
from tastypie.utils import make_naive
from edc_quota.client.models import QuotaMixin, Quota as ClientQuota
from edc_quota.controller.models import Client, ControllerQuotaHistory, ControllerQuota
from edc_quota.controller.controller import Controller
from collections import defaultdict

tz = pytz.timezone(settings.TIME_ZONE)


class DummyController(Controller):

    def get_client_model_count(self, name):
        return 5

    def post_client_quota(self, name):
        pass


# class DummyControllerWithPut(Controller):
#
#     def post_client_quota(self, name):
#         self.api_client.post(
#             self.client[name].post_url,
#             format='json',
#             data=data,
#             authentication=self.get_credentials()
#         )


class TestQuotaModel(QuotaMixin, models.Model):

    field1 = models.CharField(max_length=10)

    field2 = models.CharField(max_length=10)

    class Meta:
        app_label = 'edc_quota_controller'


class TestController(TestCase):

    def setUp(self):

        self.quota = ControllerQuota.objects.create(
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
        self.assertIsNotNone(quota_history.last_contact)

    def test_post_all(self):
        controller = DummyController(self.quota)
        controller.get_all()
        controller.post_all()
        for client in Client.objects.all():
            self.assertEqual(client.last_contact, controller.quota_history.last_contact)
            self.assertEqual(client.target, 0)
            self.assertEqual(client.expires_datetime, controller.quota_history.expires_datetime)
        controller = DummyController(self.quota)
        controller.quota.target = 100
        controller.get_all()
        controller.post_all()
        for client in Client.objects.all():
            self.assertEqual(client.last_contact, controller.quota_history.last_contact)
            self.assertGreaterEqual(client.target, 5)
            self.assertEqual(client.expires_datetime, controller.quota_history.expires_datetime)

    def test_expired_quota(self):
        self.quota = ControllerQuota.objects.create(
            app_label='edc_quota_controller',
            model_name='TestQuotaModel',
            target=3,
            expires_datetime=timezone.now() - timedelta(days=1)
        )
        with self.assertRaises(ObjectDoesNotExist):
            DummyController(self.quota)

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


class TestResource(ResourceTestCase):

    def setUp(self):
        super(TestResource, self).setUp()

        self.username = 'erik'
        self.password = 'pass'
        self.user = User.objects.create_user(self.username, 'erik@example.com', self.password)

        self.quota = ControllerQuota.objects.create(
            app_label='edc_quota_controller',
            model_name='TestQuotaModel',
            target=3,
            expires_datetime=timezone.now() + timedelta(days=1)
        )

        Client.objects.create(
            hostname='erik',
            app_label='edc_quota_controller',
            model_name='TestQuotaModel',
            is_active=True)

    def get_credentials(self):
        return self.create_basic(username=self.username, password=self.password)

    def test_api_post_list(self):
        """Asserts api can be used to create a new Quota instance on the client."""

        self.assertEqual(ClientQuota.objects.count(), 0)

        resource_data = {
            'app_label': 'edc_quota_client',
            'model_name': 'Quota',
            'target': 30,
            'expires_datetime': make_naive(timezone.now()).isoformat(),
        }
        self.assertHttpCreated(
            self.api_client.post(
                '/api/v1/quota/',
                format='json',
                data=resource_data,
                authentication=self.get_credentials()
            )
        )
        self.assertEqual(ClientQuota.objects.count(), 1)

#     def test_controller_roundtrip(self):
#         self.assertEqual(ClientQuota.objects.count(), 0)
#         controller = Controller(self.quota)
