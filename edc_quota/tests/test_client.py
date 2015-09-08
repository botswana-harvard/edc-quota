import pytz

from datetime import date, timedelta

from django.conf import settings
from django.db import models
from django.test import TestCase
from django.contrib import admin
from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase
from tastypie.utils import make_naive
from tastypie.models import ApiKey

from edc_quota.client.models import QuotaMixin, Quota, QuotaManager
from edc_quota.client.exceptions import QuotaReachedError


tz = pytz.timezone(settings.TIME_ZONE)


class TestQuotaModel(QuotaMixin, models.Model):

    field1 = models.CharField(max_length=10)

    field2 = models.CharField(max_length=10)

    objects = QuotaManager()

    def save(self, *args, **kwargs):
        self.field2 = 'erik'
        super(TestQuotaModel, self).save(*args, **kwargs)

    class Meta:
        app_label = 'edc_quota'


class TestQuotaModelAdmin(admin.ModelAdmin):
    model = TestQuotaModel
admin.site.register(TestQuotaModel, TestQuotaModelAdmin)


class TestQuota(TestCase):

    def test_quota_model_create(self):
        quota = Quota.objects.create(
            app_label='edc_quota',
            model_name='TestQuotaModel',
            target=2,
            expiration_date=date.today() + timedelta(days=1)
        )
        self.assertEqual(
            Quota.objects.filter(
                app_label='edc_quota',
                model_name='TestQuotaModel').last(), quota)
        self.assertEqual(
            Quota.objects.filter(
                app_label='edc_quota',
                model_name='TestQuotaModel',
            ).last(), quota)

    def test_quota_create_with_manager(self):
        expiration_date = date.today() + timedelta(days=1)
        TestQuotaModel.objects.set_quota(10, expiration_date)
        TestQuotaModel.objects.set_quota(5, expiration_date + timedelta(days=1))
        last_quota = Quota.objects.filter(
            app_label='edc_quota',
            model_name='TestQuotaModel').order_by('quota_datetime').last()
        self.assertEqual(TestQuotaModel.objects.get_quota()[0:3],
                         (last_quota.target, last_quota.model_count, last_quota.expiration_date))
        self.assertEqual(TestQuotaModel.objects.get_quota()[0:3],
                         (5, 0, expiration_date + timedelta(days=1)))

    def test_quota_pk(self):
        """Assert test model picks the correct quota_pk on created and updated."""
        TestQuotaModel.objects.set_quota(2, date.today() + timedelta(days=1))
        test_model = TestQuotaModel()
        test_model.save()
        pk1 = TestQuotaModel.objects.get_quota().pk
        self.assertEqual(test_model.quota_pk, pk1)
        TestQuotaModel.objects.set_quota(2, date.today() + timedelta(days=1))
        pk2 = TestQuotaModel.objects.get_quota().pk
        self.assertNotEqual(pk1, pk2)
        test_model.save()
        self.assertEqual(test_model.quota_pk, pk1)
        test_model = TestQuotaModel()
        test_model.save()
        self.assertEqual(test_model.quota_pk, pk2)

    def test_quota_model_count_with_save(self):
        """Asserts model_count is incremented on save / created."""
        TestQuotaModel.objects.set_quota(2, date.today() + timedelta(days=1))
        quota = TestQuotaModel.objects.get_quota()
        self.assertEqual(quota.model_count, 0)
        test_model = TestQuotaModel()
        test_model.save()
        quota = TestQuotaModel.objects.get_quota()
        self.assertEqual(quota.model_count, 1)
        test_model.save()
        quota = TestQuotaModel.objects.get_quota()
        self.assertEqual(quota.model_count, 1)
        test_model = TestQuotaModel()
        test_model.save()
        quota = TestQuotaModel.objects.get_quota()
        self.assertEqual(quota.model_count, 2)

    def test_quota_model_count_with_create(self):
        """Asserts model_count is incremented on save / created."""
        TestQuotaModel.objects.set_quota(2, date.today() + timedelta(days=1))
        quota = TestQuotaModel.objects.get_quota()
        self.assertEqual(quota.model_count, 0)
        test_model = TestQuotaModel.objects.create()
        quota = TestQuotaModel.objects.get_quota()
        self.assertEqual(quota.model_count, 1)
        test_model.save()
        quota = TestQuotaModel.objects.get_quota()
        self.assertEqual(quota.model_count, 1)
        test_model = TestQuotaModel.objects.create()
        quota = TestQuotaModel.objects.get_quota()
        self.assertEqual(quota.model_count, 2)

    def test_quota_reached(self):
        """Asserts mixin save method works with model save."""
        TestQuotaModel.objects.set_quota(2, date.today() + timedelta(days=1))
        test_model = TestQuotaModel()
        test_model.save()
        self.assertTrue(test_model.field2, 'erik')
        quota = TestQuotaModel.objects.get_quota()
        self.assertEqual(quota.model_count, 1)
        test_model = TestQuotaModel()
        test_model.save()
        quota = TestQuotaModel.objects.get_quota()
        self.assertEqual(quota.model_count, 2)
        self.assertRaises(QuotaReachedError, TestQuotaModel.objects.create)
        self.assertEqual(TestQuotaModel.objects.all().count(), 2)
        self.assertEqual(TestQuotaModel.objects.quota_reached, True)

    def test_quota_reached_manager_method(self):
        """Asserts mixin save method works with model save."""
        today = date.today()
        for m in range(0, 10):
            TestQuotaModel.objects.set_quota(m + 1, date.today() + timedelta(days=m))
        for m in range(0, 5):
            test_model = TestQuotaModel()
            test_model.save()
        self.assertEqual(TestQuotaModel.objects.quota_reached, False)
        for m in range(0, 5):
            test_model = TestQuotaModel()
            test_model.save()
        self.assertEqual(TestQuotaModel.objects.get_quota()[0:3], (10, 10, today + timedelta(days=9)))
        self.assertEqual(TestQuotaModel.objects.quota_reached, True)

    def test_increase_quota(self):
        """Asserts quota is reached and then can be changed up."""
        TestQuotaModel.objects.set_quota(2, date.today() + timedelta(days=1))
        TestQuotaModel.objects.create()
        TestQuotaModel.objects.create()
        self.assertRaises(QuotaReachedError, TestQuotaModel.objects.create)
        TestQuotaModel.objects.set_quota(3, date.today() + timedelta(days=1))
        self.assertIsInstance(TestQuotaModel.objects.create(), TestQuotaModel)
        self.assertRaises(QuotaReachedError, TestQuotaModel.objects.create)

    def test_decrease_quota(self):
        """Asserts quota is reached and then can be changed down."""
        TestQuotaModel.objects.set_quota(2, date.today())
        TestQuotaModel.objects.create()
        TestQuotaModel.objects.create()
        self.assertRaises(QuotaReachedError, TestQuotaModel.objects.create)
        TestQuotaModel.objects.set_quota(1, date.today())
        self.assertRaises(QuotaReachedError, TestQuotaModel.objects.create)
        self.assertEqual(TestQuotaModel.objects.get_quota().target, 1)

    def test_expired_quota(self):
        """Asserts quota is reached if expired."""
        TestQuotaModel.objects.set_quota(2, date.today() - timedelta(days=2))
        self.assertRaises(QuotaReachedError, TestQuotaModel.objects.create)

    def test_large_quota(self):
        TestQuotaModel.objects.set_quota(100, date.today() + timedelta(days=1))
        for _ in range(0, 100):
            TestQuotaModel.objects.create()
        self.assertRaises(QuotaReachedError, TestQuotaModel.objects.create)
        model_count = TestQuotaModel.objects.get_quota().model_count
        self.assertEqual(model_count, 100)


class QuotaResourceTest(ResourceTestCase):

    def setUp(self):
        super(QuotaResourceTest, self).setUp()

        self.username = 'erik'
        self.password = 'pass'
        self.user = User.objects.create_user(self.username, 'erik@example.com', self.password)
        self.api_key = ApiKey.objects.get_or_create(user=self.user)[0].key
        TestQuotaModel.objects.set_quota(100, date.today() + timedelta(days=1))

        self.quota = Quota.objects.last()

    def get_credentials(self):
        return self.create_apikey(username=self.username, api_key=self.api_key)

    def test_get_list_unauthorzied(self):
        self.assertHttpUnauthorized(self.api_client.get('/api/v1/quota/', format='json'))

    def test_get_list_json(self):
        """Asserts api returns a full list."""
        for _ in range(0, 3):
            TestQuotaModel.objects.create()
        resp = self.api_client.get('/api/v1/quota/', format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 1)
        quota_json = {
            'target': 100,
            'expiration_date': self.quota.expiration_date.isoformat(),
            'model_count': 3,
            'quota_datetime': make_naive(self.quota.quota_datetime).isoformat(),
            'id': self.quota.pk,
            'app_label': 'edc_quota',
            'model_name': 'TestQuotaModel',
            'resource_uri': '/api/v1/quota/{0}/'.format(self.quota.pk)
        }
        self.assertEqual(self.deserialize(resp)['objects'][0], quota_json)

    def test_get_with_model_name_json(self):
        """Asserts api returns a full list."""
        for _ in range(0, 2):
            TestQuotaModel.objects.create()
        resp = self.api_client.get(
            '/api/v1/quota/',
            app_label='edc_quota',
            model_name='TestQuotaModel',
            format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 1)
        self.assertEqual(self.deserialize(resp)['objects'][0], {
            'id': self.quota.pk,
            'target': 100,
            'model_count': 2,
            'app_label': 'edc_quota',
            'expiration_date': self.quota.expiration_date.isoformat(),
            'model_name': 'TestQuotaModel',
            'quota_datetime': make_naive(self.quota.quota_datetime).isoformat(),
            'resource_uri': '/api/v1/quota/{0}/'.format(self.quota.pk)
        })

    def test_post_unauthenticated(self):
        """Assert the api does put"""
        resp = self.api_client.post('/api/v1/quota/', format='json', data={})
        self.assertHttpUnauthorized(resp)
