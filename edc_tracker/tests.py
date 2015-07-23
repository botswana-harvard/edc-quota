from django.test import TestCase

from models import Tracker, SiteTracker
from tracker_helper import TrackerHelper


class TestTracker(TestCase):

    def setUp(self):
        pass

    def test_tracker(self):

        tracker_helper = TrackerHelper()
        tracker_helper.app_label = 'edc_tracker'
        tracker_helper.master_server_name = 'central'
        tracker_helper.model_filter_field_attr = 'master_server_name'
        tracker_helper.model_filter_value = 'central'
        tracker_helper.model_site_field_attr = 'gaborone'
        tracker_helper.tracked_model = Tracker
        tracker_helper.url = 'http://localhost:8000/tracker/'
        tracker_helper.value_limit = 400
        tracker_helper.tracked_value = 0
        tracker_helper.auth = ('django', '1234')
        tracker_helper.tracker()
        trackers = Tracker.objects.all()
        self.assertEqual(trackers.count(), 1)

    def test_site_tracker(self):

        tracker_helper = TrackerHelper()
        tracker_helper.app_label = 'edc_tracker'
        tracker_helper.master_server_name = 'central'
        tracker_helper.site_name = 'gaborone'
        tracker_helper.model_filter_field_attr = 'app_name'
        tracker_helper.model_filter_value = 'edc_tracker'
        tracker_helper.model_site_field_attr = 'site_name'
        tracker_helper.tracked_model = SiteTracker
        tracker_helper.url = 'http://localhost:8000/tracker/'
        tracker_helper.value_limit = 400
        tracker_helper.tracked_value = 0
        tracker_helper.auth = ('django', '1234')
        tracker_helper.site_tracker()
        site_trackers = SiteTracker.objects.all()
        self.assertEqual(site_trackers.count(), 1)
