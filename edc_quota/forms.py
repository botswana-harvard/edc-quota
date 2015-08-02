from django import forms

from .models import MasterQuota, ClientQuota


class MasterQuotaForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(ClientQuota, self).clean()
        return cleaned_data

    class Meta:
        model = MasterQuota
        fields = '__all__'


class ClientQuotaForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(ClientQuota, self).clean()
        return cleaned_data

    class Meta:
        model = ClientQuota
        fields = '__all__'
