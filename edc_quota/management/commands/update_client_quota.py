import sys

from django.utils import timezone
from django.core.management.base import BaseCommand

from edc_quota.controller import Controller, ControllerQuota


class Command(BaseCommand):

    args = ('--post_all', '--post_client')

    help = 'Update the client quota'

    def add_arguments(self, parser):

        parser.add_argument(
            '--clients', action='store_true', default=False,
            help='Update one or more specific clients'
        )

    def handle(self, *args, **options):

        self.clients = None
        sys.stdout.write('Begin ...')
        sys.stdout.flush()
        if options.get('clients', ''):
            self.clients = args[0].split(',')
            sys.stdout.write('Updating clients {} only'.format(args[0]))
            sys.stdout.flush()
        for quota in ControllerQuota.objects.filter(is_active=True, expires_datetime__lte=timezone.now()):
            try:
                sys.stdout.flush()
                controller = Controller(quota, clients=self.clients)
                sys.stdout.write('  Updating {}'.format(quota))
                controller.get_all()
                controller.post_all()
                sys.stdout.write('  Done updating {}'.format(quota))
                sys.stdout.flush()
            except ControllerQuota.DoesNotExist:
                pass
        sys.stdout.write('Done.')
        sys.stdout.flush()
