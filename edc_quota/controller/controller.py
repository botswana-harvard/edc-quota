import requests

from datetime import timedelta
from django.utils import timezone


from .models import Client, ControllerQuota, ControllerQuotaHistory


class Controller(object):
    """A class to control or manage quotas between a group of offline clients.

    For example:
        quota = Quota.objects.get(...)
        controller = Controller(quota)
        controller.get_all()
        controller.post_all()

    """
    def __init__(self, quota=None, app_label=None, model_name=None, auth=None):
        self.clients = {}
        self.auth = auth
        if quota:
            self.quota = ControllerQuota.objects.get(
                pk=quota.pk,
                is_active=True,
                expires_datetime__gte=timezone.now())
        else:
            self.quota = ControllerQuota.objects.get(
                app_label=app_label,
                model_name=model_name,
                is_active=True,
                expires_datetime__gte=timezone.now())
        self.quota_history = ControllerQuotaHistory.objects.create(
            quota=self.quota,
            expires_datetime=timezone.now() + timedelta(days=1))
        self.register_all()

    def register_all(self):
        for client in Client.objects.filter(
                app_label=self.quota.app_label,
                model_name=self.quota.model_name,
                is_active=True):
            self.register(client)

    def register(self, client):
        self.clients[client.name] = client

    def get_all(self):
        """Contacts all registered clients and updates the Quota model."""
        last_contact = timezone.now()
        total_model_count = 0
        clients_contacted = []
        for name in self.clients:
            self.clients.get(name).model_count = self.get_client_model_count(name)
            if self.clients.get(name).model_count:
                self.clients.get(name).last_contact = last_contact
                total_model_count += self.clients.get(name).model_count
                clients_contacted.append(name)
            self.clients.get(name).save()
        self.quota_history.model_count = total_model_count
        self.quota_history.last_contact = last_contact
        self.quota_history.clients_contacted = ','.join(clients_contacted)
        self.quota_history.save()
        self.set_new_targets()

    def post_all(self):
        """posts the new quota targets on the clients."""
        for name in self.quota_history.clients_contacted_list:
            data = dict(
                app_label=self.clients.get(name).app_label,
                model_name=self.clients.get(name).model_name,
                target=self.clients.get(name).target,
                expires_datetime=self.clients.get(name).expires_datetime
            )
            self.post_client_quota(name, data)

    def get_client_model_count(self, name):
        """Fetches one clients model_count over the REST api."""
        request = requests.get(self.clients.get(name).url)
        objects = request.json()['objects']
        try:
            model_count = objects[0].get('model_count', None)
        except IndexError:
            model_count = None
        return model_count

    def set_new_targets(self):
        """Calculates new quota targets for all contacted clients."""
        allocation = self.quota.target - self.quota_history.model_count
        client_count = len(self.quota_history.clients_contacted_list)
        remainder = allocation % client_count if allocation > 0 else 0
        for name in self.quota_history.clients_contacted_list:
            self.clients.get(name).target, remainder = self.target(allocation, client_count, remainder)
            self.clients.get(name).expires_datetime = self.quota_history.expires_datetime
            self.clients.get(name).save()

    def target(self, allocation, client_count, remainder):
        if allocation <= 0 or client_count == 0:
            return 0, 0
        extra = 0
        if remainder > 0:
            remainder -= 1
            extra = 1
        return int(allocation / client_count) + extra, remainder

    def post_client_quota(self, name, data):
        """Creates an instance of quota in the client."""
        requests.post(self.clients.get(name).post_url, data=data, auth=self.auth)
