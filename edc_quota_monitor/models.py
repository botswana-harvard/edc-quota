from django.db import models


class MasterQuota(models.Model):

    app_name = models.CharField(max_length=100)

    master_server_url = models.CharField(
        max_length=100,
        help_text=("The url of the central server, e.g central.bhp.org.bw.")
    )

    model_name = models.CharField(max_length=150)

    master_quota = models.IntegerField(default=0, editable=True)

    quota_limit = models.IntegerField(default=0, editable=True)

    def __str__(self):
        return "{}_{}".format(self.model_name, self.master_server_url)

    class Meta:
        app_label = 'edc_quota_monitor'


class ClientQuota(models.Model):

    quota = models.IntegerField(default=0, editable=True)

    client_hostname = models.CharField(max_length=150)

    client_url = models.CharField(max_length=150)

    model_name = models.CharField(max_length=150)

    app_name = models.CharField(max_length=100)

    quota_limit = models.IntegerField(
        default=0,
        editable=True,
        help_text=("Daily quota limit")
    )

    def __str__(self):
        return "{}_{}".format(self.model_name, self.client_hostname)

    class Meta:
        app_label = 'edc_quota_monitor'
