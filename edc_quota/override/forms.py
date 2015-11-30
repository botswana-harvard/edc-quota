from django import forms

from .code import Code


class OverrideForm(forms.Form):

    override_request = forms.CharField(required=True)

    def clean(self):
        cleaned_data = super(OverrideForm, self).clean()
        if cleaned_data.get('override_request'):
            cleaned_data['override_request'] = Code(cleaned_data.get('override_request')).validation_code
        return cleaned_data
