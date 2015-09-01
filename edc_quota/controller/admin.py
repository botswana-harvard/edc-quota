from django.contrib import admin

from .models import ControllerQuota, ControllerQuotaHistory, Client


@admin.register(ControllerQuota)
class ControllerQuotaAdmin(admin.ModelAdmin):
    date_hierarchy = 'expiration_date'
    fields = ('model_name', 'app_label', 'target', 'expiration_date', 'max_allocation', 'is_active')
    list_display = ('model_name', 'app_label', 'target', 'expiration_date', 'max_allocation', 'is_active')
    list_filter = ('is_active', 'app_label', 'expiration_date')
    search_fields = ('model_name', )


@admin.register(ControllerQuotaHistory)
class ControllerQuotaHistoryAdmin(admin.ModelAdmin):
    date_hierarchy = 'quota_datetime'
    fields = ('quota', 'expiration_date', 'last_contact', 'clients_contacted', 'model_count')
    list_display = ('quota', 'expiration_date', 'last_contact', 'clients_contacted', 'model_count')
    list_filter = ('expiration_date', 'last_contact')
    search_fields = ('clients_contacted', )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    date_hierarchy = 'expiration_date'
    fields = (
        'hostname', 'app_label', 'model_name', 'port', 'last_contact', 'target',
        'expiration_date', 'is_active'
    )
    list_display = (
        'hostname', 'app_label', 'model_name', 'port', 'last_contact', 'target',
        'expiration_date', 'is_active'
    )
    list_filter = ('app_label', 'model_name', 'is_active', 'expiration_date')
    search_fields = ('app_label', 'model_name')
