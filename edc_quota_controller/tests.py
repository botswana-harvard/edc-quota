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


class TestResource(ResourceTestCase):

    def setUp(self):
        super(TestResource, self).setUp()

        # Create a user.
        self.username = 'daniel'
        self.password = 'pass'
        self.user = User.objects.create_user(self.username, 'daniel@example.com', self.password)

        self.client_quota_1 = ClientQuota.objects.get(slug='first-post')

        self.detail_url = '/api/quota/entry/{0}/'.format(self.entry_1.pk)

        self.post_data = {
            'user': '/api/quota/user/{0}/'.format(self.user.pk),
            'title': 'Second Post!',
            'slug': 'second-post',
            'created': '2012-05-01T22:05:12'
        }

    def get_credentials(self):
        return self.create_basic(username=self.username, password=self.password)

    def test_get_list_unauthorzied(self):
        self.assertHttpUnauthorized(self.api_client.get('/api/v1/entries/', format='json'))

    def test_get_list_json(self):
        resp = self.api_client.get('/api/v1/entries/', format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)

        # Scope out the data for correctness.
        self.assertEqual(len(self.deserialize(resp)['objects']), 12)
        # Here, we're checking an entire structure for the expected data.
        self.assertEqual(self.deserialize(resp)['objects'][0], {
            'pk': str(self.entry_1.pk),
            'user': '/api/v1/user/{0}/'.format(self.user.pk),
            'title': 'First post',
            'slug': 'first-post',
            'created': '2012-05-01T19:13:42',
            'resource_uri': '/api/v1/entry/{0}/'.format(self.entry_1.pk)
        })
