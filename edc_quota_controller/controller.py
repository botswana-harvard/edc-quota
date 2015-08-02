import requests

from django.utils import timezone

from .models import Client, Quota, QuotaHistory


class Controller(object):
    """A class to control or manage quotas between a group of offline clients.

    For example:
        quota = Quota.objects.get(...)
        controller = Controller(quota)
        controller.fetch_all()
        controller.update_all()

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
        self.last_contact = None
        self.total_count = 0
        self.clients_contacted = []
        self.register_all()

    def register_all(self):
        for client in Client.objects.filter(
                app_label=self.app_label,
                model_name=self.model_name,
                is_active=True):
            self.register(client)

    def register(self, client):
        self.clients[client.name] = client

    def fetch_all(self):
        """Contacts all registered clients and updates the Quota model."""
        self.last_contact = timezone.now()
        self.total_count = 0
        self.clients_contacted = []
        for name in self.clients:
            request = requests.get(self.clients.get(name).url)
            objects = request.json()['objects']
            try:
                self.clients.get(name).model_count = objects[0].get('model_count', None)
                self.clients.get(name).last_contact = self.last_contact
            except IndexError:
                self.clients.get(name).model_count = None
            self.total_count += self.clients.get(name).model_count
            self.clients_contacted.append(name)
        QuotaHistory.objects.create(
            quota=self.quota,
            app_label=self.app_label,
            model_name=self.model_name,
            total_count=self.total_count,
            last_contact=self.last_contact,
            clients_contacted=','.join(self.clients_contacted),
        )

    def update_all(self):
        """Contacts all registered clients and sets their new quota targets."""
        quota_history = self.calculate()
        for name in quota_history.clients_contacted.split(','):
            self.clients.get(name).new_quota_target = quota_history.new_quota_target
            self.clients.get(name).new_quota_expires = quota_history.new_quota_expires
        for name in self.clients:
            # add put request here
            pass

    def calculate(self):
        """Calculates new targets, updates QuotaHistory and returns the new QuotaHistory instance."""
        quota_history = QuotaHistory.objects.filter(quota=self.quota).last()
        quota_history.new_quota_target = '?'  # add calculation for a new target for all contacted clients
        quota_history.new_quota_expires = '?'  # add an expiration date e.g. tomorrow end of day
        quota_history.save()
        quota_history = QuotaHistory.objects.filter(quota=self.quota).last()
        return quota_history
