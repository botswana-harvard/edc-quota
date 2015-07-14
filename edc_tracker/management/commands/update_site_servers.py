import csv
import os

from django.core.management.base import BaseCommand, CommandError

from apps.bcpp_tracker.models import Tracker


class Command(BaseCommand):
    """Creates a csv files of 4 files containing plot list of 75, 25, 20 and 5 percent. """

    APP_NAME = 0
    MODEL_NAME = 1
    args = '<community name e.g otse>'
    help = 'Update site tracked values from the central server.'

    def handle(self, *args, **options):
#         if not args or len(args) < 1:
#             raise CommandError('Missing \'using\' parameters.')
        community_name = args[0]
