import sys

from datetime import date
from django.core.management.base import BaseCommand

from edc_quota.controller.controller import Controller
from edc_quota.controller.models import ControllerQuota


class Command(BaseCommand):

    help = 'Update the quotas'

    def handle(self, *args, **options):
        self.clients = None
        sys.stdout.write('Begin ...\n')
        sys.stdout.flush()
        try:
            self.clients = args[0].split(',')
            sys.stdout.write('Updating clients \'{}\' only\n'.format('\', \''.join(self.clients)))
        except IndexError:
            pass
        sys.stdout.flush()
        quotas = ControllerQuota.objects.filter(is_active=True, expiration_date__gte=date.today())
        if quotas.count() == 0:
            sys.stdout.write('Nothing to do! Try creating a controller quota.\n')
        else:
            sys.stdout.write('Found {} controller quota.\n'.format(quotas.count()))
        for quota in quotas:
            sys.stdout.flush()
            controller = Controller(quota, clients=self.clients)
            sys.stdout.write('Updating {}\n'.format(quota))
            controller.get_all()
            controller.post_all()
            sys.stdout.write('Done updating {}\n'.format(quota))
            sys.stdout.flush()
        sys.stdout.write('Done.\n')
        sys.stdout.flush()
