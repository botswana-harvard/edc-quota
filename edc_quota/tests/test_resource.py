from datetime import date, timedelta
from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase
from tastypie.models import ApiKey

from edc_quota.client.models import Quota as ClientQuota
from edc_quota.controller.models import Client, ControllerQuota
from edc_quota.controller.controller import Controller
from edc_quota.controller.exceptions import ControllerError


class TestResource(ResourceTestCase):

    def setUp(self):
        super(TestResource, self).setUp()

        self.username = 'erik'
        self.password = 'pass'
        self.user = User.objects.create_user(self.username, 'erik@example.com', self.password)
        self.api_client_key = ApiKey.objects.get_or_create(user=self.user)[0].key
        self.quota = ControllerQuota.objects.create(
            app_label='edc_quota',
            model_name='TestQuotaModel2',
            target=3,
            start_date=date.today(),
            expiration_date=date.today() + timedelta(days=1)
        )

        Client.objects.create(
            hostname='erik',
            app_label='edc_quota',
            model_name='TestQuotaModel2',
            is_active=True)

    def get_credentials(self):
        return self.create_apikey(username=self.username, api_key=self.api_client_key)

    def test_api_post_list(self):
        """Asserts api can be used to create a new Quota instance on the client."""

        self.assertEqual(ClientQuota.objects.count(), 0)

        resource_data = {
            'app_label': 'edc_quota',
            'model_name': 'Quota',
            'target': 30,
            'start_date': date.today(),
            'expiration_date': date.today()
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

    def test_controller_quota_not_active_or_expired_raises(self):
        self.quota.is_active = False
        self.quota.save()
        with self.assertRaises(ControllerError):
            Controller(self.quota)
        self.quota.is_active = True
        self.quota.expiration_date = date.today() - timedelta(days=1)
        self.quota.save()
        with self.assertRaises(ControllerError):
            Controller(self.quota)

    def test_post_url_format(self):
        controller = Controller(self.quota, username='erik')
        self.assertEqual(['api_key', 'username'], sorted(controller.auth.keys()))
