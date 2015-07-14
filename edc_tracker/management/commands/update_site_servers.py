from django.core.management.base import BaseCommand


class Command(BaseCommand):

    APP_NAME = 0
    MODEL_NAME = 1
    args = '<community name e.g otse>'
    help = 'Update site tracked values from the central server.'

    def handle(self, *args, **options):
        pass
