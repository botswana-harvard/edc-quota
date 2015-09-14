import requests

from datetime import date, timedelta
from django.utils import timezone

from .models import Client, ControllerQuota, ControllerQuotaHistory


class Controller(object):
    """A class to control or manage quotas between a group of offline clients.

    For example:
        quota = ControllerQuota.objects.get(...)
        controller = Controller(quota)
        controller.get_all()
        controller.post_all()

    """
    def __init__(self, quota, clients=None, auth=None):
        self.clients = {}
        self.auth = auth
        try:
            if quota:
                self.quota = ControllerQuota.objects.get(
                    pk=quota.pk,
                    is_active=True,
                    start_date__lte=date.today(),
                    expiration_date__gte=date.today())
            self.quota_history = ControllerQuotaHistory.objects.create(
                quota=self.quota,
                expiration_date=self.expiration_date_on_client)
            if clients:
                for hostname in clients:
                    client = Client.objects.get(
                        hostname=hostname,
                        app_label=self.quota.app_label,
                        model_name=self.quota.model_name,
                        is_active=True)
                    self.register(client)
            else:
                self.register_all()
        except (ControllerQuota.DoesNotExist, AttributeError) as e:
            raise ControllerQuota.DoesNotExist(
                'Quota for model \'{}\' is not active, expired or does not exist. Got {}'.format(
                    quota, str(e)))

    def register_all(self):
        for client in Client.objects.filter(
                app_label=self.quota.app_label,
                model_name=self.quota.model_name,
                is_active=True):
            self.register(client)

    def register(self, client=None, hostname=None):
        try:
            hostname = client.hostname
        except AttributeError:
            client = Client.objects.get(
                hostname=hostname,
                app_label=self.quota.app_label,
                model_name=self.quota.model_name,
                is_active=True)
        self.clients[hostname] = client

    @property
    def expiration_date_on_client(self):
        if self.quota.duration:
            return date.today() + timedelta(days=self.quota.duration)
        else:
            return self.quota.expiration_date

    def get_all(self):
        """Contacts all registered clients and updates the Quota model."""
        contacted = timezone.now()
        total_model_count = 0
        clients_contacted = []
        for name in self.clients:
            self.clients.get(name).model_count = self.get_client_model_count(name)
            if self.clients.get(name).model_count:
                self.clients.get(name).contacted = contacted
                total_model_count += self.clients.get(name).model_count
                clients_contacted.append(name)
            self.clients.get(name).save()
        self.quota_history.model_count = total_model_count
        self.quota_history.contacted = contacted
        self.quota_history.clients_contacted = ','.join(clients_contacted)
        self.quota_history.save()
        self.set_new_targets()

    def post_all(self):
        """posts the new quota targets on the clients."""
        for name in self.quota_history.clients_contacted_list:
            self.post_client_quota(name)

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
            self.clients.get(name).start_date = self.quota_history.start_date
            self.clients.get(name).expiration_date = self.quota_history.expiration_date
            self.clients.get(name).save()

    def target(self, allocation, client_count, remainder):
        if allocation <= 0 or client_count == 0:
            return 0, 0
        extra = 0
        if remainder > 0:
            remainder -= 1
            extra = 1
        return int(allocation / client_count) + extra, remainder

    def post_client_quota(self, name):
        """Creates an instance of quota in the client."""
        data = dict(
            app_label=self.clients.get(name).app_label,
            model_name=self.clients.get(name).model_name,
            target=self.clients.get(name).target,
            start_date=self.clients.get(name).start_date,
            expiration_date=self.clients.get(name).expiration_date
        )
        requests.post(self.clients.get(name).post_url, data=data, auth=self.auth)
