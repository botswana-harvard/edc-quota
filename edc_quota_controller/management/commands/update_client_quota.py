from django.core.management.base import BaseCommand
from edc_quota_client.models import Quota
from edc_quota_controller.controller import Controller

from datetime import datetime, timedelta, time
from django.core.exceptions import MultipleObjectsReturned, ImproperlyConfigured
from edc_quota_controller.models import Client


class Command(BaseCommand):

    args = ('--post_all', '--post_client')

    help = 'Update the client quota'

    def add_arguments(self, parser):

        parser.add_argument(
            '--post_all', action='store_true', default=False,
            help='Update all quota clients'
        )
        parser.add_argument(
            '--post_client', action='store_true', default=False,
            help='Update a particular client'
        )

    def handle(self, *args, **options):

        if options.get('post_all', ''):
            self.post_all()
        elif options.get('post_client', ''):
            self.post_client(args[0])

    def post_all(self):
        try:
            today = datetime.now().date()
            tomorrow = today + timedelta(1)
            today_start = datetime.combine(today, time())
            today_end = datetime.combine(tomorrow, time())
            quota = Quota.objects.get(is_active=True, expires_datetime__range=(today_start, today_end))
            controller = Controller(quota)
            controller.post_all()
            self.stdout.write('All clients have been updated successfully.')
        except MultipleObjectsReturned:
                raise ImproperlyConfigured("There are multiple quota active. make sure there is only one quota active.")
        except Quota.DoesNotExist:
            raise ImproperlyConfigured("Quota does not exists. create a quota to update clients with.")

    def post_client(self, hostname):
        try:
            today = datetime.now().date()
            tomorrow = today + timedelta(1)
            today_start = datetime.combine(today, time())
            today_end = datetime.combine(tomorrow, time())
            quota = Quota.objects.get(is_active=True, expires_datetime__range=(today_start, today_end))
            controller = Controller(quota)
            controller.clients = {}
            client = Client.objects.get(hostname=hostname)
            controller.register(client)
            controller.post_all()
            self.stdout.write('{0} was updated successfully.'.format(hostname))
        except MultipleObjectsReturned:
                raise ImproperlyConfigured("There are multiple quota active. make sure there is only one quota active.")