from django.db import models


class MasterQuota(models.Model):

    app_name = models.CharField(
        max_length=100,
    )

    master_server_url = models.CharField(
        max_length=100,
        help_text=("The url of the central server, e.g central.bhp.org.bw.")
    )

    model = models.CharField(
        max_length=150,
    )

    master_quota = models.IntegerField(
        default=0,
        editable=True,
    )

    def __str__(self):
        return "{}_{}".format(self.model, self.master_server_url)

    class Meta:
        app_label = 'edc_quota_monitor'


class ClientQuota(models.Model):

    master_quota = models.ForeignKey(MasterQuota)

    quota = models.IntegerField(
        default=0,
        editable=True,
    )

    client_hostname = models.CharField(
        max_length=150,
    )

    model = models.CharField(
        max_length=150,
    )

    app_name = models.CharField(
        max_length=100,
    )

    def __str__(self):
        return "{}_{}".format(self.model, self.app_name)

    class Meta:
        app_label = 'edc_quota_monitor'
