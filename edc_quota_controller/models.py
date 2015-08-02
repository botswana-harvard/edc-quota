from django.db import models


class QuotaModel(models.Model):

    app_label = models.CharField(max_length=25)

    model_name = models.CharField(max_length=25)

    quota = models.IntegerField()

    is_active = models.BooleanField()

    def __str__(self):
        return "{}_{}".format(self.app_label, self.model_name)

    class Meta:
        app_label = 'edc_quota'


class Client(models.Model):
    """Clients to populate registry on the Controller."""

    hostname = models.CharField(max_length=25)

    url = models.CharField(max_length=150, null=True)

    is_active = models.BooleanField()

    def __str__(self):
        return "{}".format(self.hostname)

    class Meta:
        app_label = 'edc_quota'
