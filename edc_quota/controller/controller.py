import json
import requests

from datetime import date
from django.utils import timezone
from django.contrib.auth.models import User
from tastypie.models import ApiKey

from .exceptions import ControllerError
from .models import Client, ControllerQuota, ControllerQuotaHistory


class Controller(object):
    """A class to control or manage quotas between a group of offline clients.

    For example:
        quota = ControllerQuota.objects.get(...)
        controller = Controller(quota)
        controller.get_all()
        controller.post_all()
    from datetime import date, timedelta
    from edc_quota.controller.models import Client, ControllerQuota
    from edc_quota.controller.controller import Controller

    client = Client(hostname='edc4.bhp.org.bw', port=8001, api_name='v1')
    controller_quota = ControllerQuota(target=10, start_date=date.today(), expiration_date=date.today() + timedelta(days=1), app_label='bcpp_subject', model_name='PimaVl')
    controller_quota.id = 1
    controller = Controller(controller_quota, [client], username='edc_quota', api_key='a817fc214f81b0e1467039e2ac61acbf99db8d47')
    """
    def __init__(self, quota, clients=None, username=None, api_name=None, api_key=None):
        self.api_name = api_name or 'v1'
        self.base_url = 'http://{hostname}:{port}/edc_quota/api/{api_name}/quota/'
        self.clients = {}
        self.auth = {}
        self.status_codes = {'get': {}, 'post': {}}
        username = username or 'edc_quota'
        try:
            user = User.objects.get(username=username)
            self.auth.update({'username': username})
            self.auth.update({'api_key': ApiKey.objects.get(user=user).key})
        except (User.DoesNotExist, ApiKey.DoesNotExist):
            self.auth.update({'username': username})
            self.auth.update({'api_key': api_key})
        try:
            if quota.is_active and quota.start_date <= date.today() and quota.expiration_date >= date.today():
                self.quota = quota
            else:
                raise ControllerError(
                    'ControllerQuota {} is not active. '
                    'Got is_active={}, start date {}, end date {}.'.format(
                        quota, quota.is_active, quota.start_date, quota.expiration_date))
            self.quota_history = ControllerQuotaHistory.objects.create(
                quota=self.quota,
                start_date=date.today(),
                expiration_date=self.quota.expiration_date)
            if clients:
                for hostname in clients:
                    try:
                        client = Client.objects.get(hostname=hostname)
                        if client.is_active:
                            self.register(client)
                    except Client.DoesNotExist as e:
                        pass
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

    def get_all(self):
        """Contacts all registered clients and updates the Quota model."""
        contacted = timezone.now()
        total_model_count = 0
        clients_contacted = []
        for hostname, client in self.clients.items():
            client.model_count = self.get_client_model_count(client) or 0
            client.contacted = contacted
            total_model_count += client.model_count
            clients_contacted.append(hostname)
            client.save()
        self.quota_history.model_count = total_model_count
        self.quota_history.contacted = contacted
        self.quota_history.clients_contacted = ','.join(clients_contacted)
        self.quota_history.save()
        if self.quota_history.clients_contacted:
            self.set_new_targets()
        else:
            print('Warning: Appears there are no clients online. New targets have not been set.')

    def post_all(self):
        """posts the new quota targets on the clients."""
        for hostname in self.quota_history.clients_contacted_list:
            self.post_client_quota(hostname)

    def get_url(self, client):
        return '{base}?format=json&app_label={app_label}&model_name={model_name}&{credentials}'.format(
            base=self.base_url.format(hostname=client.hostname, port=client.port, api_name=self.api_name),
            app_label=self.quota.app_label,
            model_name=self.quota.model_name.lower(),
            credentials=self.credentials)

    def get_request(self, client):
        hostname = client.hostname
        try:
            request = requests.get(self.get_url(client))
            self.status_codes['get'].update({hostname: request.status_code})
        except ConnectionError:
            self.status_codes['get'].update({hostname: None})
            request = None
        return request

    def get_client_model_count(self, client):
        """Fetches one clients model_count over the REST api."""
        request = self.get_request(client)
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

    @property
    def credentials(self):
        return 'username={username}&api_key={api_key}'.format(
            username=self.auth.get('username'),
            api_key=self.auth.get('api_key'))

    def post_url(self, name, port):
        return '{base}/?format=json&{credentials}'.format(
            base=self.base_url.format(hostname=name, port=port, api_name=self.api_name),
            credentials=self.credentials
        )

    def post_client_quota(self, hostname):
        """Creates an instance of quota in the client."""
        client = self.clients.get(hostname)
        data = dict(
            app_label=self.quota.app_label,
            model_name=self.quota.model_name.lower(),
            target=self.clients.get(hostname).target,
            start_date=self.clients.get(hostname).start_date.isoformat(),
            expiration_date=self.clients.get(hostname).expiration_date.isoformat())
        request = requests.post(self.post_url(client.hostname, client.port), data=json.dumps(data))
        try:
            status_code = request.status_code
        except AttributeError:
            status_code = None
        self.status_codes['post'].update({hostname: status_code})
        return request
