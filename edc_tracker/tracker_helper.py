import requests
import json

from datetime import datetime

from django.db.models import Q

from models import Tracker, SiteTracker


class TrackerHelper(object):
    """Calculates and updates tracked value.
    """

    def __init__(self):
        """Sets value_type, and tracker server name."""

        self.model_filter_field_attr = None
        self.model_site_field_attr = None
        self.model_filter_value = None
        self.master_server_name = None
        self.tracked_model = None
        self.site_name = None
        self.url = None
        self.auth = None
        self.value_limit = None

    def master_tracked_value(self):
        """Returns the total number of instances of a tracked model"""

        tracked_value = self.tracked_model.objects.filter(
            Q(**{self.model_filter_field_attr: self.model_filter_value})
        ).count()
        return tracked_value

    def site_tracked_value(self):
        """Return the total of instances of site tracked model."""

        site_tracked_value = self.tracked_model.objects.filter(
            Q(**{self.model_filter_field_attr: self.model_filter_value,
                 self.model_site_field_attr: self.site_name}),
        ).count()
        return site_tracked_value

    def update_remote_tracker(self):
        """Update a remote tracker."""

        tracker_data = self.tracker()
        requests.post(self.url, data=json.dumps(tracker_data), self.auth)

    def update_site_tracker(self):
        """Update site tracker."""

        site_tracker_data = self.site_tracker()
        requests.post(self.url, data=json.dumps(site_tracker_data), self.auth)

    def tracker(self):
        """Returns a tracker."""
        try:
            tracker = Tracker.objects.get(
                master_server_name=self.master_server_name
            )
        except Tracker.DoesNotExist:
            Tracker.objects.create(
                start_date=datetime.today(),
                tracked_value=self.master_tracked_value(),
                master_server_name=self.master_server_name,
                model=self.tracked_model,
                app_name=self.tracked_model._meta.app_label,
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
                Q(**{self.model_site_field_attr: self.site_name}),
                tracker=self.tracker()
            )
            SiteTracker.objects.filter(tracker='')
        except SiteTracker.DoesNotExist:
            SiteTracker.objects.create(
                start_date=datetime.today(),
                tracked_value=self.site_tracked_value(),
                site_name=self.site_name,
                model=self.tracked_model,
                app_name=self.tracked_model._meta.app_label,
                update_date=datetime.today(),
                tracker=self.tracker(),
                value_limit=self.value_limit
            )
            site_tracker = SiteTracker.objects.get(
                Q(**{self.model_site_field_attr: self.site_name}),
                tracker=self.tracker()
            )
        return site_tracker
