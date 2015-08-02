import requests

from .models import ClientQuota, MasterQuota


class Controller(object):

    def __init__(self, quota):
        self.quota = quota

    def register(self, client):
        self.clients[client.name] = client

    def update_counts(self):
        for name in self.clients:
            request = requests.get(self.clients.get(name).url)
            objects = request.json()['objects']
            try:
                self.clients.get(name).count = objects[0].get('count', None)
            except IndexError:
                self.clients.get(name).count = None

#     def calculate_master_quota(self):
#         """Calculate quota for the master."""
#         master_quota = self.master_quota()
#         model_instance_count = get_model(
#             master_quota.model_name,
#             master_quota.app_name
#         ).objects.filter(**self.model_filter_dict).count()
#         return master_quota.quota_limit - model_instance_count
# 
#     def calculate_clients_quotas(self):
#         """Calculate a quota for each client."""
#         total_clients = len(self.clients)
#         quota_per_client = (self.calculate_master_quota()/total_clients)
#         # Leave reminders for re-allocating
#         if quota_per_client > 3 and not quota_per_client < 10:
#             quota_per_client -= 1
#         elif quota_per_client < 10:
#             quota_per_client = 10
#         return quota_per_client
# 
#     def allocate_quota(self):
#         """Allocate client quota."""
#         pass
# 
#     def by_pass_quota(self):
#         """Bypass quota limit."""
#         pass
