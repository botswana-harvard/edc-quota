# from django.contrib import admin
# 
# from .forms import ClientQuotaForm, MasterQuotaForm
# from .models import MasterQuota, ClientQuota
# 
# 
# class ClientQuotaAdmin(admin.ModelAdmin):
#     form = ClientQuotaForm
#     fields = (
#         'quota',
#         'client_hostname',
#         'master_quota',
#         'client_url'
#         'model_name',
#         'app_name'
#     )
#     list_display = (
#         'quota',
#         'client_hostname',
#         'client_url',
#         'model_name',
#         'app_name'
#     )
#     list_filter = ('client_hostname', 'model_name')
#     search_fields = ['client_hostname']
# admin.site.register(ClientQuota, ClientQuotaAdmin)
# 
# 
# class MasterQuotaAdmin(admin.ModelAdmin):
#     form = MasterQuotaForm
#     instructions = []
#     list_per_page = 15
#     fields = (
#         'app_name',
#         'master_server_url',
#         'model_name',
#         'master_quota',
#         'quota_limit'
#     )
#     list_per_page = 15
#     list_display = (
#         'app_name',
#         'master_server_url',
#         'model_name',
#         'master_quota',
#         'quota_limit',
#     )
#     list_filter = ('master_server_url', 'model_name')
#     search_fields = ['master_server_url']
# admin.site.register(MasterQuota, MasterQuotaAdmin)
