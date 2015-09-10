import re
from django.core.management.base import BaseCommand, CommandError

from edc_quota.configure import Configure


class Command(BaseCommand):

    args = ('shared_apikey', )
    help = 'Setup edc_quota account, api key and model add and change permissions'

    def handle(self, *args, **options):
        try:
            shared_apikey = args[0]
            if not re.match('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', shared_apikey):
                CommandError('Invalid shared apikey. Got {}'.format(shared_apikey))
        except IndexError:
            shared_apikey = None
        configure = Configure(shared_apikey=shared_apikey)
        print('User \'edc_quota\' has been created')
        print('User \'edc_quota\': added to group \'edc_quota_api\'')
        print('User \'edc_quota\': apikey {}'.format(configure.apikey))
