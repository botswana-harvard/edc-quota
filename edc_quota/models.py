import django
from django.db import models

if (django.VERSION[0], django.VERSION[1]) == (1, 6):
    from .client import Quota
    from .controller import ControllerQuota, ControllerQuotaHistory, Client
    from .override import OverrideModel
