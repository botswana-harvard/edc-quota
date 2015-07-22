from datetime import datetime
import factory

from models import SiteTracker
from tracker_factory import TrackerFactory


class SiteTrackerFactory(factory.DjangoModelFactory):
    class Meta:
        model = SiteTracker

    start_date = datetime.today()
    tracked_value = 0
    site_name = 'mmandunyane'
    model = 'TestModel'
    app_name = 'app_label'
    update_date = datetime.today()
    tracker = TrackerFactory()
    value_limit = 400
