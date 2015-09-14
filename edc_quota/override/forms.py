from django import forms


class OverridetForm(forms.Form):

    override_request = forms.CharField(required=True)
    override_code = forms.CharField()

#     def clean(self):
#         cleaned_data = super(OverridetForm, self).clean()
#
#         if cleaned_data.get('override_request'):
#             clean_data[]
