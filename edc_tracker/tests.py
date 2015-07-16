from django.test import TestCase
from django.db import models


from tracker_helper import TrackerHelper


class ModelTracked(models.Model):

    MODEL_CHOICES = (
        ('setting_1', 'setting 1'),
        ('setting_2', 'setting 2'),
    )

    value_type = models.CharField(
        verbose_name="Type mobile or household setting",
        choices=MODEL_CHOICES,
        max_length=150,
    )

    site = models.CharField(
        verbose_name="Type mobile or household setting",
        default='test_site',
        max_length=150,
    )

    class Meta:
        app_label = 'model_test'


class TestTracker(TestCase):

    def setUp(self):
        pass

    def test_tracker_method(self):

        tracker_helper = TrackerHelper()
        tracker_helper.model_filter_field_attr = 'value_type'
        tracker_helper.model_site_field_attr = 'site'
        tracker_helper.model_filter_value = 'setting_1'
        tracker_helper.master_server_name = 'central'
        tracker_helper.site_name = 'test_site'
        tracker_helper.tracked_model = ModelTracked
        tracker = tracker_helper.tracker()
        self.assertEqual(tracker.count(), 1)
