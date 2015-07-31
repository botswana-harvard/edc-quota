from django import forms

from edc_tracker.models import Tracker, SiteTracker


class TrackerForm(forms.ModelForm):

    class Meta:
        model = Tracker
        fields = '__all__'


class SiteTrackerForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(SiteTrackerForm, self).clean()
        return cleaned_data

    class Meta:
        model = SiteTracker
        fields = '__all__'
