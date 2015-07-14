from django.test import TestCase

from ..classes import TrackerHelper
from ..models import Tracker, SiteTracker


class TestTracker(TestCase):

    app_label = 'bcpp_tracking'
    community = 'rakops'

    def setUp(self):
        pass

    def test_central_community_tracker(self):

        tracker = TrackerHelper()
        tracker.update_central_tracker()
        self.assertEqual(1, Tracker.objects.all().count())
