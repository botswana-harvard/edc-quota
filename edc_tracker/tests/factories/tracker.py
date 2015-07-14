import factory
from datetime import date, datetime
from edc.base.model.tests.factories import BaseUuidModelFactory
from ...models import Tracker


class TrackerFactory(BaseUuidModelFactory):
    FACTORY_FOR = Tracker
