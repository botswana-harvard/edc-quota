from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key

from .client.models import Quota
from .controller.models import Client, ControllerQuota, ControllerQuotaHistory
from .override.models import OverrideModel

models.signals.post_save.connect(create_api_key, sender=User)
