from django.db.models.loading import get_model

from edc_quota_monitor.models import ClientQuota, MasterQuota


class QoutaMonitor(object):
    """Calculates and updates andmonitors quota value.
    """

    def __init__(
            self,
            client_hostname,
            model_name,
            master_server_url,
            clients,
            model_filter_dict):
        """Class variables..."""

        self.client_hostname = client_hostname
        self.model_name = model_name
        self.master_server_url = master_server_url
        self.clients = clients    # A list of clients
        self.model_filter_dict = model_filter_dict

    def client_quota(self):
        """Return client quota."""
        return ClientQuota.objects.get(
            client_hostname=self.client_hostname
        ).quota

    def client_quota_instance(self):
        """Return client quota instance."""
        return ClientQuota.objects.get(
            client_hostname=self.client_hostname,
            model_name=self.model_name
        )

    def master_quota(self):
        """Return master server quota."""
        return MasterQuota.objects.get(
            master_server_url=self.master_server_url,
            model_name=self.model_name
        ).master_quota

    def master_quota_instance(self):
        """Return master server quota instance."""
        return MasterQuota.objects.get(
            master_server_url=self.master_server_url,
            model_name=self.model_name
        )

    def quota_limit(self):
        """Return the master quota limit."""
        return MasterQuota.objects.get(
            master_server_url=self.master_server_url,
            model_name=self.model_name
        ).quota_limit

    def calculate_master_quota(self):
        """Calculate quota for the master."""
        master_quota = self.master_quota()
        model_instance_count = get_model(
            master_quota.model_name,
            master_quota.app_name
        ).objects.filter(**self.model_filter_dict).count()
        return master_quota.quota_limit - model_instance_count

    def calculate_clients_quotas(self):
        """Calculate a quota for each client."""
        total_clients = len(self.clients)
        quota_per_client = (self.calculate_master_quota()/total_clients)
        # Leave reminders for re-allocating
        if quota_per_client > 3 and not quota_per_client < 10:
            quota_per_client -= 1
        elif quota_per_client < 10:
            quota_per_client = 10
        return quota_per_client

    def allocate_quota(self):
        """Allocate client quota."""
        pass

    def by_pass_quota(self):
        """Bypass quota limit."""
        pass
