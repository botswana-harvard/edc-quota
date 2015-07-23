from datetime import datetime

from django.views.generic import View
from django.shortcuts import render

from models import Tracker, SiteTracker


class TrackerView(View):

    def get_context_data(self, **kwargs):
        self.context = super(TrackerView, self).get_context_data(**kwargs)
        return self.context

    def post(self, request, *args, **kwargs):
        """Allows a POST -- without the class returns a 405 error."""

        # Update tracker
        tracker_data = request.POST('tracker_dict')
        tracker = Tracker.objects.get(
            value_type=tracker_data['value_type'],
            master_server_name=tracker_data['master_server_name']
        )
        tracker.tracked_value = tracker_data['tracked_value']
        tracker.update_date = datetime.today()
        tracker.save(update_fields=['tracked_value', 'update_date'])

        # Update site_tracker
        site_tracker_data = request.POST('site_tracker_data')
        tracker = Tracker.objects.get(
            value_type=site_tracker_data['value_type'],
            master_server_name=site_tracker_data['master_server_name']
        )
        site_tracker = SiteTracker.objects.get(
            site_name=site_tracker_data['site_name'],
            tracker=tracker
        )
        site_tracker.tracked_value = site_tracker_data['tracked_value']
        site_tracker.update_date = datetime.today()
        site_tracker.save(update_fields=['tracked_value', 'update_date'])
        return render(
            request,
            self.template_name,
            self.get_context_data(**kwargs)
        )

    def get(self, request, *args, **kwargs):
        """Allows a GET -- without the class returns a 405 error."""
        return render(
            request,
            self.template_name,
            self.get_context_data(**kwargs)
        )
