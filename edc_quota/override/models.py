from django.db import models


class OverrideModel(models.Model):

    request_code = models.CharField(max_length=10, unique=True)

    override_code = models.CharField(max_length=10)

    app_label = models.CharField(max_length=25)

    model_name = models.CharField(max_length=25)

    validated = models.BooleanField(default=False)

    instance_pk = models.CharField(max_length=36, null=True)

    @property
    def used(self):
        return True if self.pk else False

    class Meta:
        app_label = 'edc_quota'
