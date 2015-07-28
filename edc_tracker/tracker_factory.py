from datetime import datetime
import factory

from edc_tracker.models import Tracker


class TrackerFactory(factory.DjangoModelFactory):
    class Meta:
        model = Tracker

    start_date = datetime.today()
    tracked_value = 0
    value_type = 'Mobile settings'
    master_server_name = 'central'
    model = 'Tracker'
    app_name = 'edc_tracker'
    update_date = datetime.today()
    value_limit = 400
