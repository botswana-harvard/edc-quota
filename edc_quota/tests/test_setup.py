from datetime import timedelta
from django.db import models
from django.utils import timezone
try:
    from django.apps import apps
    models_list = apps.get_app_config('edc_quota').get_models()
except ImportError:
    from django.db.models import get_models, get_app
    models_list = get_models(get_app('edc_quota'))
from django.test import TestCase
from django.contrib.auth.models import Group
from tastypie.models import ApiKey

from edc_quota.configure import Configure
from edc_quota.client.models import QuotaMixin, QuotaManager


class TestQuotaModel3(QuotaMixin, models.Model):

    QUOTA_TARGET = 10
    START_DATE = timezone.now()
    EXPIRATION_DATE = timezone.now() + timedelta(days=365)

    field1 = models.CharField(max_length=10)

    field2 = models.CharField(max_length=10)

    quota = QuotaManager()

    objects = models.Manager()

    class Meta:
        app_label = 'edc_quota'


class TestSetup(TestCase):

    def test_create_user_with_apikey(self):
        configure = Configure()
        self.assertEqual(ApiKey.objects.get(user=configure.user).key, configure.apikey)

    def test_user_has_group(self):
        configure = Configure()
        self.assertEqual(Group.objects.get(name=configure.groupname), configure.group)

    def test_has_permissions(self):
        configure = Configure()
        configure.user.user_permissions.filter()
        for model in models_list:
            self.assertEqual(
                [p.codename for p in configure.group.permissions.filter(
                 content_type__app_label='edc_quota',
                 content_type__model=model._meta.object_name.lower()).order_by('codename')],
                ['add_{}'.format(model._meta.object_name.lower()),
                 'change_{}'.format(model._meta.object_name.lower())])

    def test_shared_apikey(self):
        controller = Configure()
        client1 = Configure(username='client1', shared_apikey=controller.apikey)
        client2 = Configure(username='client2', shared_apikey=controller.apikey)
        client3 = Configure(username='client3', shared_apikey=controller.apikey)
        self.assertEqual(controller.apikey, client1.apikey)
        self.assertEqual(controller.apikey, client2.apikey)
        self.assertEqual(controller.apikey, client3.apikey)

    def test_create_client_quotas_if_possible(self):
        controller = Configure()
        controller.create_initial_client_quota(TestQuotaModel3)
        quota = TestQuotaModel3.quota.get_quota()
        self.assertIsNotNone(quota)
        self.assertEqual(quota.target, 10)
