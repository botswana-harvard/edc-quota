import requests

from django.utils import timezone

from .models import Client, Quota, QuotaHistory


class Controller(object):
    """A class to control or manage quotas between a group of offline clients.

    For example:
        quota = Quota.objects.get(...)
        controller = Controller(quota)
        controller.get_all()
        controller.put_all()

    """
    def __init__(self, quota=None, app_label=None, model_name=None):
        if quota:
            self.quota = Quota.objects.get(
                pk=quota.pk,
                is_active=True,
                expires_datetime__gte=timezone.now())
        else:
            self.quota = Quota.objects.get(
                app_label=app_label,
                model_name=model_name,
                is_active=True,
                expires_datetime__gte=timezone.now())
        self.clients = {}
        self.last_contact = None
        self.total_count = 0
        self.clients_contacted = []
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
        self.last_contact = timezone.now()
        self.total_count = 0
        self.clients_contacted = []
        for name in self.clients:
            self.clients.get(name).model_count = self.get_client_model_count(name)
            if self.clients.get(name).model_count:
                self.clients.get(name).last_contact = self.last_contact
                self.total_count += self.clients.get(name).model_count
                self.clients_contacted.append(name)
            self.clients.get(name).save()
        QuotaHistory.objects.create(
            quota=self.quota,
            total_count=self.total_count,
            last_contact=self.last_contact,
            clients_contacted=','.join(self.clients_contacted),
        )

    def get_client_model_count(self, name):
        """Fetches one clients model_count over the REST api."""
        request = requests.get(self.clients.get(name).url)
        objects = request.json()['objects']
        try:
            model_count = objects[0].get('model_count', None)
        except IndexError:
            model_count = None
        return model_count

    def put_all(self):
        """Puts the new quota targets on the clients."""
        quota_history = QuotaHistory.objects.create(quota=self.quota)
        quota_history = self.calculate(quota_history)
        try:
            self.clients_contacted = quota_history.clients_contacted.split(',')
        except AttributeError:
            self.clients_contacted = []
        for name in self.clients_contacted:
            self.clients.get(name).target = quota_history.target
            self.clients.get(name).expires_datetime = quota_history.expires_datetime
            self.clients.get(name).save()
            self.put_new_client_quota(name)

    def calculate(self, quota_history):
        """Calculates new targets, updates QuotaHistory and returns the new QuotaHistory instance."""
        quota_history.target = -1  # add calculation for a new target for all contacted clients
        quota_history.expires_datetime = timezone.now()  # add an expiration date e.g. tomorrow end of day
        quota_history.save()
        quota_history = QuotaHistory.objects.get(pk=quota_history.pk)
        return quota_history

    def put_new_client_quota(self, name):
        pass  # put to the tastypie quota resource on the client
