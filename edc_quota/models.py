from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key

from edc_quota.client.models import Quota
from edc_quota.controller.models import Client, ControllerQuota, ControllerQuotaHistory
from edc_quota.override.models import OverrideModel

models.signals.post_save.connect(create_api_key, sender=User)
