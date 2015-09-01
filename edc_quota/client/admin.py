from django.contrib import admin

from .models import Quota


@admin.register(Quota)
class QuotaAdmin(admin.ModelAdmin):
    date_hierarchy = 'quota_datetime'
    list_display = ('model_name', 'app_label', 'target', 'expiration_date', 'model_count', 'is_active')
    list_filter = ('is_active', 'app_label', 'expiration_date', 'quota_datetime')
    search_fields = ('model_name', )
