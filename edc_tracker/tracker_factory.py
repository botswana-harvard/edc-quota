from datetime import datetime
import factory

from models import Tracker


class TrackerFactory(factory.DjangoModelFactory):
    class Meta:
        model = Tracker

    start_date = datetime.today()
    tracked_value = 0
    master_server_name = 'central'
    model = 'TestModel'
    app_name = 'TrackerModel'
    update_date = datetime.today()
    value_limit = 400
