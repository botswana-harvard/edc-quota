from django.db import models


class OverrideModel(models.Model):

    request_code = models.CharField(max_length=10, unique=True)

    override_code = models.CharField(max_length=10)

    app_label = models.CharField(max_length=25, editable=False)

    model_name = models.CharField(max_length=25, editable=False)

    validated = models.BooleanField(default=False, editable=False)

    instance_pk = models.CharField(max_length=36, null=True, editable=False)

    def __str__(self):
        return self.request_code

    @property
    def used(self):
        return True if self.instance_pk else False

    class Meta:
        app_label = 'edc_quota'
        db_table = 'edc_quota_override'
        verbose_name = 'Override'
