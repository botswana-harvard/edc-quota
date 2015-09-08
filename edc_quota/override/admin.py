from django.contrib import admin

from .models import OverrideModel


class OverrideAdmin(admin.ModelAdmin):
    pass
admin.site.register(OverrideModel, OverrideAdmin)
