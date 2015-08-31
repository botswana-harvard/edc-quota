import sys

from datetime import datetime, timedelta, time

from django.core.management.base import BaseCommand
from django.core.exceptions import MultipleObjectsReturned, ImproperlyConfigured

from edc_quota.client import Quota
from edc_quota.controller import Controller, Client


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
        sys.stdout.write('Begin post all ...')
        sys.stdout.flush()
        for quota in Quota.objects.filter(is_active=True):
            try:
                sys.stdout.write('  Updating {}'.format(quota))
                sys.stdout.flush()
                controller = Controller(quota)
                controller.post_all()
                sys.stdout.write('  Done updating {}'.format(quota))
                sys.stdout.flush()
            except Quota.DoesNotExist:
                pass
        sys.stdout.write('Done.')
        sys.stdout.flush()

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
