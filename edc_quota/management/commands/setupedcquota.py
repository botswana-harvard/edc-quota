from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'Setup edc_quota account, api key and model add and change permissions'

    def handle(self, *args, **options):
        pass
