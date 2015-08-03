from django.contrib import admin

from .models import Quota, QuotaHistory


@admin.register(Quota)
class QuotaAdmin(admin.ModelAdmin):
    date_hierarchy = 'expires_datetime'
    list_display = ('model_name', 'app_label', 'target', 'expires_datetime', 'max_allocation', 'is_active')
    list_filter = ('is_active', 'app_label', 'expires_datetime')
    search_fields = ('model_name', )


@admin.register(QuotaHistory)
class QuotaHistoryAdmin(admin.ModelAdmin):
    date_hierarchy = 'quota_datetime'
    list_display = ('quota', 'expires_datetime', 'last_contact', 'clients_contacted', 'model_count')
    list_filter = ('expires_datetime', 'last_contact')
    search_fields = ('clients_contacted', )
