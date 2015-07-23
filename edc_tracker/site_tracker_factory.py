from datetime import datetime
import factory

from models import SiteTracker
from tracker_factory import TrackerFactory


class SiteTrackerFactory(factory.DjangoModelFactory):
    class Meta:
        model = SiteTracker

    start_date = datetime.today()
    tracked_value = 0
    site_name = 'gaborone'
    model = SiteTracker
    app_name = 'edc_tracker'
    update_date = datetime.today()
    tracker = TrackerFactory()
