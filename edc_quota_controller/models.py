from django.db import models
from django.utils import timezone


class Quota(models.Model):
    """Controllers quota model."""

    app_label = models.CharField(max_length=25)

    model_name = models.CharField(max_length=25)

    target = models.IntegerField()

    expires_datetime = models.DateTimeField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{}".format(self.model_name)

    class Meta:
        app_label = 'edc_quota_controller'


class QuotaHistory(models.Model):
    """Controllers quota history model."""

    get_latest_by = "quota_datetime"

    quota = models.ForeignKey(Quota)

    total_count = models.IntegerField(default=0)

    clients_contacted = models.CharField(
        max_length=500,
        null=True)

    target = models.IntegerField(null=True)

    expires_datetime = models.DateTimeField(null=True)

    last_contact = models.DateTimeField(null=True)

    quota_datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{}".format(self.model_name)

    class Meta:
        app_label = 'edc_quota_controller'


class Client(models.Model):
    """Clients to populate registry on the Controller."""

    hostname = models.CharField(max_length=25)

    app_label = models.CharField(max_length=25)

    model_name = models.CharField(max_length=25)

    port = models.IntegerField(default=80)

    api_name = models.CharField(max_length=25, default='v1')

    last_contact = models.DateTimeField(null=True)

    target = models.IntegerField(default=0)

    expires_datetime = models.DateTimeField(null=True)

    is_active = models.BooleanField()

    def __str__(self):
        return "{}".format(self.hostname)

    @property
    def url(self):
        return 'http://{}:{}/api/{}/?app_label={}&model_name={}&format=json'.format(
            self.hostname, self.port, self.api_name, self.app_label, self.model_name)

    @property
    def name(self):
        return self.hostname

    class Meta:
        app_label = 'edc_quota_controller'
