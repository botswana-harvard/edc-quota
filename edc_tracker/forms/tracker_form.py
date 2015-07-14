from edc.base.form.forms import BaseModelForm

from ..models import Tracker, SiteTracker


class TrackerForm(BaseModelForm):

    class Meta:
        model = Tracker


class SiteTrackerForm(BaseModelForm):

    def clean(self):
        cleaned_data = super(SiteTrackerForm, self).clean()
        return cleaned_data

    class Meta:
        model = SiteTracker
