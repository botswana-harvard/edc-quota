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

    def update_master_tracker(self):
        """Update the tracker on the master server."""
        tracker = self.tracker()
        tracker.tracked_value = self.master_tracked_value()
        tracker.update_date = datetime.today()
        tracker.save(update_fields=['tracked_value', 'update_date'])

    def update_site_tracker(self):
        """Update the site tracker on the master server or site server."""
        site_tracker = self.site_tracker()
        site_tracker.tracked_value = self.site_tracked_value()
        site_tracker.update_date = datetime.today()
        site_tracker.save(update_fields=['tracked_value', 'update_date'])

    def update_remote_tracker(self):
        """Update a remote tracker from the master server."""

        self.update_master_tracker()
        tracker = self.tracker()
        tracker_dict = {
            'tracked_value': tracker.tracked_value,
            'value_type': tracker.value_type,
            'master_server_name': tracker.master_server_name
        }
        requests.post(self.url, data=json.dumps(tracker_dict))

    def update_remote_site_tracker(self):
        """Update a remote site tracker."""

        self.update_site_tracker()
        site_tracker = self.site_tracker()
        value_type = site_tracker.tracker.value_type
        master_server_name = site_tracker.tracker.master_server_name
        site_tracker_dict = {
            'tracked_value': site_tracker.tracked_value,
            'site_name': site_tracker.site_name,
            'tracker': site_tracker.tracker,
            'value_type': value_type,
            'master_server_name': master_server_name
        }
        requests.post(self.url, data=json.dumps(site_tracker_dict))

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
