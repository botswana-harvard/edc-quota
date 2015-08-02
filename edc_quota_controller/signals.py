# import socket
# 
# from django.db.models.loading import get_model
# from django.db.models.signals import pre_save, post_save
# from django.dispatch import receiver
# 
# from edc_quota_monitor.models import ClientQuota
# 
# 
# class QuotaLimitReached():
#     pass
# 
# 
# @receiver(post_save, weak=False, dispatch_uid="monitored_model_on_post_save")
# def monitored_model_on_post_save(sender, instance, raw, created, using, **kwargs):
#     """Updates client quota once a model being monitored is saved."""
#     client_quota = ClientQuota.objects.get(
#         client_hostname=socket.gethostname()
#     )
#     app_name = client_quota.app_name
#     model_name = client_quota.model_name
#     if not raw:
#         if isinstance(instance, get_model(model_name, app_name)):
#             if client_quota.quota > 0:
#                 client_quota.quota -= 1    # Decrement by 1.
#                 client_quota.save()
# 
# 
# @receiver(pre_save, weak=False, dispatch_uid="monitored_model_on_pre_save")
# def monitored_model_on_pre_save(sender, instance, raw, using, **kwargs):
#     """"Validate if the monitored model's quota limit is not reached."""
#     client_quota = ClientQuota.objects.get(
#         client_hostname=socket.gethostname()
#     )
#     app_name = client_quota.app_name
#     model_name = client_quota.model_name
#     if not raw:
#         if isinstance(instance, get_model(model_name, app_name)):
#             if client_quota.quota > 0:
#                 pass
#             else:
#                 raise QuotaLimitReached("message.")
