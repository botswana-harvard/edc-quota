from django.contrib import admin

from .models import ControllerQuota, ControllerQuotaHistory, Client


class ControllerQuotaAdmin(admin.ModelAdmin):
    date_hierarchy = 'expiration_date'
    fields = ('model_name', 'app_label', 'target', 'start_date', 'expiration_date', 'max_allocation', 'is_active')
    list_display = ('model_name', 'app_label', 'target', 'start_date',
                    'expiration_date', 'max_allocation', 'is_active')
    list_filter = ('is_active', 'app_label', 'start_date', 'expiration_date')
    search_fields = ('model_name', )
admin.site.register(ControllerQuota, ControllerQuotaAdmin)


class ControllerQuotaHistoryAdmin(admin.ModelAdmin):
    date_hierarchy = 'quota_datetime'
    fields = ('quota', 'start_date', 'expiration_date', 'contacted', 'clients_contacted', 'model_count')
    list_display = ('quota', 'start_date', 'expiration_date', 'contacted', 'clients_contacted', 'model_count')
    list_filter = ('start_date', 'expiration_date', 'contacted')
    search_fields = ('clients_contacted', )
admin.site.register(ControllerQuotaHistory, ControllerQuotaHistoryAdmin)


class ClientAdmin(admin.ModelAdmin):
    date_hierarchy = 'expiration_date'
    fields = ('hostname', 'app_label', 'model_name', 'port', 'is_active')
    list_display = ('hostname', 'contacted', 'quota', 'app_label', 'model_name', 'target', 'model_count')
    list_filter = ('app_label', 'model_name', 'is_active', 'start_date', 'expiration_date', 'contacted', 'hostname')
    search_fields = ('app_label', 'model_name')
admin.site.register(Client, ClientAdmin)
