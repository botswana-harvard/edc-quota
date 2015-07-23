from django.test import TestCase

from models import Tracker, SiteTracker
from tracker_helper import TrackerHelper
from tracker_factory import TrackerFactory
from site_tracker_factory import SiteTrackerFactory


class TestTracker(TestCase):

    def setUp(self):
        pass

    def test_tracker1(self):

        tracker_helper = TrackerHelper()
        tracker_helper.app_label = 'edc_tracker'
        tracker_helper.master_server_name = 'central'
        tracker_helper.value_type = 'Mobile settings'
        tracker_helper.tracked_model = Tracker
        tracker_helper.value_limit = 400
        tracker_helper.master_filter_dict = {
            'master_server_name': tracker_helper.master_server_name,
            'value_type': tracker_helper.value_type
        }
        tracker_helper.tracker()
        trackers = Tracker.objects.all()
        self.assertEqual(trackers.count(), 1)

    def test_tracker2(self):

        tracker_helper = TrackerHelper()
        tracker_helper.master_server_name = 'central'
        tracker_helper.value_type = 'Mobile settings'
        TrackerFactory()
        tracker = tracker_helper.tracker()
        tracker1 = Tracker.objects.get(
            master_server_name='central',
            value_type='Mobile settings'
        )
        self.assertEqual(tracker, tracker1)

    def test_site_tracker(self):

        tracker_helper = TrackerHelper()
        tracker_helper.app_label = 'edc_tracker'
        tracker_helper.master_server_name = 'central'
        tracker_helper.value_type = 'Mobile settings'
        tracker_helper.value_limit = 400
        tracker_helper.master_filter_dict = {
            'tracker__value_type': tracker_helper.value_type
        }
        tracker_helper.site_name = 'gaborone'
        tracker_helper.tracked_model = SiteTracker
        tracker_helper.site_filter_dict = {'site_name': 'gaborone'}
        tracker_helper.site_tracker()
        site_trackers = SiteTracker.objects.all()
        self.assertEqual(site_trackers.count(), 1)

    def test_site_tracker1(self):

        tracker_helper = TrackerHelper()
        tracker_helper.app_label = 'edc_tracker'
        tracker_helper.master_server_name = 'central'
        tracker_helper.value_type = 'Mobile settings'
        TrackerFactory(model='SiteTracker')
        tracker_helper.site_name = 'gaborone'
        tracker_helper.tracked_model = SiteTracker
        tracker_helper.site_filter_dict = {'site_name': 'gaborone'}
        tracker_helper.site_tracker()
        site_trackers = SiteTracker.objects.all()
        self.assertEqual(site_trackers.count(), 1)

    def test_site_tracker2(self):

        tracker_helper = TrackerHelper()
        tracker_helper.app_label = 'edc_tracker'
        tracker_helper.master_server_name = 'central'
        tracker_helper.site_name = 'gaborone'
        tracker_helper.value_type = 'Mobile settings'
        TrackerFactory(model='SiteTracker')
        tracker1 = Tracker.objects.get(
            master_server_name='central',
            value_type='Mobile settings'
        )
        tracker_helper.site_filter_dict = {
            'tracker': tracker1,
            'site_name': tracker_helper.site_name
        }
        tracker_helper.tracked_model = SiteTracker
        SiteTrackerFactory(tracker=tracker1)
        tracker_helper.site_tracker()
        site_trackers = SiteTracker.objects.all()
        self.assertEqual(site_trackers.count(), 1)
