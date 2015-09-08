from django.contrib import admin

from .code import Code
from .models import OverrideModel


class OverrideAdmin(admin.ModelAdmin):

    fields = ('request_code', 'override_code', )

    list_display = ('request_code', 'validated', 'app_label', 'model_name')

    list_filter = ('validated', 'app_label', 'model_name')

    def get_form(self, request, obj=None, **kwargs):
        form = super(OverrideAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['request_code'].initial = str(Code())
        return form

admin.site.register(OverrideModel, OverrideAdmin)
