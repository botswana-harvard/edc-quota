from django.contrib import admin
from django.core.urlresolvers import resolve
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

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

    def response_add(self, request, obj, post_url_continue=None):
        """This makes the response after adding go to another apps changelist for some model"""
        path = resolve(request.GET.get('next'))
        return HttpResponseRedirect(reverse(path.view_name))

admin.site.register(OverrideModel, OverrideAdmin)
