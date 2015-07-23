import requests
import json

from datetime import datetime

from models import Tracker, SiteTracker
from django.core.exceptions import ImproperlyConfigured


class TrackerHelper(object):
    """Calculates and updates tracked value.
    """

    def __init__(self):
        """Sets value_type, and tracker server name."""

        self.master_server_name = None
        self.tracked_model = None
        self.app_label = None
        self.site_name = None
        self.value_type = None
        self.url = None
        self.auth = None
        self.value_limit = None
        self.master_filter_dict = {}
        self.site_filter_dict = {}

    def master_tracked_value(self):
        """Returns the total number of instances of a tracked model"""
        if not self.master_filter_dict:
            raise ImproperlyConfigured(
                'Specify the class master_filter_dict attributes.'
            )
        tracked_value = self.tracked_model.objects.filter(
            **self.master_filter_dict
        ).count()
        return tracked_value

    def site_tracked_value(self):
        """Return the total of instances of site tracked model."""
        if not self.site_filter_dict:
            raise ImproperlyConfigured(
                'Specify the class site_filter_dict attributes.'
            )
        site_tracked_value = self.tracked_model.objects.filter(
            **self.site_filter_dict
        ).count()
        return site_tracked_value

    def update_remote_tracker(self):
        """Update a remote tracker."""

        tracker_data = self.tracker()
        requests.post(self.url, data=json.dumps(tracker_data))

    def update_site_tracker(self):
        """Update site tracker."""

        site_tracker_data = self.site_tracker()
        requests.post(self.url, data=json.dumps(site_tracker_data))
#         print(r.status_code, r.reason)

    def tracker(self):
        """Returns a tracker."""
        try:
            tracker = Tracker.objects.get(
                master_server_name=self.master_server_name,
                value_type=self.value_type,
            )
        except Tracker.DoesNotExist:
            Tracker.objects.create(
                start_date=datetime.today(),
                tracked_value=self.master_tracked_value(),
                master_server_name=self.master_server_name,
                model=self.tracked_model,
                app_name=self.app_label,
                value_type=self.value_type,
                update_date=datetime.today(),
                value_limit=self.value_limit
            )
            tracker = Tracker.objects.get(
                master_server_name=self.master_server_name
            )
        return tracker

    def site_tracker(self):
        """Returns site tracker."""
        try:
            site_tracker = SiteTracker.objects.get(
                site_name=self.site_name,
                tracker=self.tracker()
            )
        except SiteTracker.DoesNotExist:
            SiteTracker.objects.create(
                start_date=datetime.today(),
                tracked_value=self.site_tracked_value(),
                site_name=self.site_name,
                model=self.tracked_model,
                app_name=self.app_label,
                update_date=datetime.today(),
                tracker=self.tracker()
            )
            site_tracker = SiteTracker.objects.get(
                site_name=self.site_name,
                tracker=self.tracker()
            )
        return site_tracker
