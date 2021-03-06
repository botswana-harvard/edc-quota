from django.db import models
from django.utils import timezone


class ControllerQuota(models.Model):
    """Controllers quota model where each instance refers to a quota that
    this controller is managing.

    For example, a quota on the controller might be an enrollment cap
    (target) of 3000 applied to the model
    subject.Enrollment."""

    app_label = models.CharField(max_length=25)

    model_name = models.CharField(max_length=25)

    target = models.IntegerField()

    start_date = models.DateField()

    expiration_date = models.DateField()

    max_allocation = models.IntegerField(
        blank=True,
        null=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.model_name

    class Meta:
        app_label = 'edc_quota'


class ControllerQuotaHistory(models.Model):
    """Controllers quota history model.

    A new instance is created each time the controller updates quotas on
    the client for 'quota'."""

    get_latest_by = "quota_datetime"

    quota = models.ForeignKey(ControllerQuota)

    model_count = models.IntegerField(
        editable=False,
        default=0)

    clients_contacted = models.CharField(
        max_length=500,
        editable=False,
        null=True)

    start_date = models.DateField(
        editable=False,
        null=True)

    expiration_date = models.DateField(
        editable=False,
        null=True)

    contacted = models.DateTimeField(
        editable=False,
        null=True)

    quota_datetime = models.DateTimeField(
        editable=False,
        default=timezone.now)

    def __str__(self):
        return str(self.quota)

    @property
    def clients_contacted_list(self):
        clients_contacted = []
        if self.clients_contacted:
            clients_contacted = self.clients_contacted.split(',')
        return clients_contacted

    class Meta:
        app_label = 'edc_quota'
        ordering = ('-quota_datetime', )


class Client(models.Model):
    """Clients to populate registry on the Controller."""

    hostname = models.CharField(max_length=25)

    port = models.IntegerField(default=80)

    api_name = models.CharField(max_length=25, default='v1')

    app_label = models.CharField(max_length=25)

    model_name = models.CharField(max_length=25)

    target = models.IntegerField(
        editable=False,
        default=0)

    model_count = models.IntegerField(
        editable=False,
        default=0)

    start_date = models.DateField(
        editable=False,
        null=True)

    expiration_date = models.DateField(
        editable=False,
        null=True)

    contacted = models.DateTimeField(
        editable=False,
        null=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{}".format(self.hostname)

    def quota(self):
        return ControllerQuota.objects.get(app_label=self.app_label, model_name=self.model_name)
    quota.short_description = 'Quota'

    @property
    def url(self):
        return 'http://{}:{}/edc_quota/api/{}/?app_label={}&model_name={}&format=json'.format(
            self.hostname, self.port, self.api_name, self.app_label, self.model_name)

    @property
    def post_url(self):
        return 'http://{}:{}/edc_quota/api/{}/{}/'.format(
            self.hostname, self.port, self.api_name, self.model_name.lower())

    @property
    def name(self):
        return self.hostname

    class Meta:
        app_label = 'edc_quota'
