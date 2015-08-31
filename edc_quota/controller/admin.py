from django.contrib import admin

from .models import ControllerQuota, ControllerQuotaHistory, Client


@admin.register(ControllerQuota)
class ControllerQuotaAdmin(admin.ModelAdmin):
    date_hierarchy = 'expires_datetime'
    list_display = ('model_name', 'app_label', 'target', 'expires_datetime', 'max_allocation', 'is_active')
    list_filter = ('is_active', 'app_label', 'expires_datetime')
    search_fields = ('model_name', )


@admin.register(ControllerQuotaHistory)
class ControllerQuotaHistoryAdmin(admin.ModelAdmin):
    date_hierarchy = 'quota_datetime'
    list_display = ('quota', 'expires_datetime', 'last_contact', 'clients_contacted', 'model_count')
    list_filter = ('expires_datetime', 'last_contact')
    search_fields = ('clients_contacted', )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    date_hierarchy = 'expires_datetime'
    list_display = (
        'hostname', 'app_label', 'model_name', 'port', 'last_contact', 'target',
        'expires_datetime', 'is_active'
    )
    list_filter = ('app_label', 'model_name', 'is_active', 'expires_datetime')
    search_fields = ('app_label', 'model_name')
