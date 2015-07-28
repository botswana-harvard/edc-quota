from django import forms

from edc_tracker.models import Tracker, SiteTracker


class BaseModelForm(forms.ModelForm):
    pass


class TrackerForm(BaseModelForm):

    class Meta:
        model = Tracker
        fields = '__all__'


class SiteTrackerForm(BaseModelForm):

    def clean(self):
        cleaned_data = super(SiteTrackerForm, self).clean()
        return cleaned_data

    class Meta:
        model = SiteTracker
        fields = '__all__'
