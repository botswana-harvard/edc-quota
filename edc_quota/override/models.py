from django.db import models


class OverrideModel(models.Model):

    request_code = models.CharField(max_length=10, unique=True, editable=False)

    override_code = models.CharField(max_length=10)

    app_label = models.CharField(max_length=25, editable=False)

    model_name = models.CharField(max_length=25, editable=False)

    validated = models.BooleanField(default=False, editable=False)

    instance_pk = models.CharField(max_length=36, null=True, editable=False)

    @property
    def used(self):
        return True if self.pk else False

    class Meta:
        app_label = 'edc_quota'
        verbose_name = 'Override'
