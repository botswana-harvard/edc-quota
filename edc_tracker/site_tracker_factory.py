from datetime import datetime
import factory

from edc_tracker.models import SiteTracker
from edc_tracker.tracker_factory import TrackerFactory


class SiteTrackerFactory(factory.DjangoModelFactory):
    class Meta:
        model = SiteTracker

    start_date = datetime.today()
    tracked_value = 0
    site_name = 'gaborone'
    model_name = 'SiteTracker'
    app_name = 'edc_tracker'
    update_date = datetime.today()
    tracker = TrackerFactory()
