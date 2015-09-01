from django.contrib import admin

from .models import Quota


@admin.register(Quota)
class QuotaAdmin(admin.ModelAdmin):
    date_hierarchy = 'quota_datetime'
    fields = ('model_name', 'app_label', 'target', 'expires_datetime', 'model_count', 'is_active')
    list_display = ('model_name', 'app_label', 'target', 'expires_datetime', 'model_count', 'is_active')
    list_filter = ('is_active', 'app_label', 'expires_datetime', 'quota_datetime')
    search_fields = ('model_name', )
