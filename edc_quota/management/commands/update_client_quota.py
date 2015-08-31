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
                sys.stdout.flush()
                controller = Controller(quota)
                sys.stdout.write('  Updating {}'.format(quota))
                controller.post_all()
                sys.stdout.write('  Done updating {}'.format(quota))
                sys.stdout.flush()
            except Quota.DoesNotExist:
                pass
        sys.stdout.write('Done.')
        sys.stdout.flush()

    def post_one(self, hostname):
        for quota in Quota.objects.filter(is_active=True):
            try:
                client = Client.objects.get(hostname=hostname)
                sys.stdout.flush()
                controller = Controller(quota)
                sys.stdout.write('  Updating {} for {}'.format(quota, client))
                controller.post_client_quota(client.hostname)
                sys.stdout.write('  Done updating {} for {}'.format(quota, client))
                sys.stdout.flush()
            except Quota.DoesNotExist:
                pass
