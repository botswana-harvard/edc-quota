from django.db import models

from edc.base.model.models import BaseModel


class Tracker(BaseModel):

    update_date = models.DateTimeField(
         verbose_name='Start Date/Time',
         null=True
        )

    is_active = models.BooleanField(
        default=True,
        help_text=("Is the tracker active."))

    central_server_name = models.CharField(
        max_length=100,
        help_text=("The name of the central server name, e.g central.")
        )

    value_type = models.CharField(
        max_length=100,
        help_text=("Type of the value being tracked.")
        )

    app_name = models.CharField(
        max_length=100,
        help_text=("App name of the value being tracked.")
        )

    model = models.CharField(
        max_length=150,
        help_text=("Model being tracked.")
        )

    tracked_value = models.IntegerField(
        default=0,
        editable=True,
        help_text=("Tracked value.")
    )

    value_limit = models.IntegerField(
        default=400,
        editable=True,
        help_text=("Limit that control the value being tracked.")
    )

    start_date = models.DateTimeField(
         verbose_name='Start Date/Time',
         null=True
        )

    end_date = models.DateTimeField(
        verbose_name='End Date/Time',
        null=True
        )

    def __unicode__(self):
        return "{}_{}".format(self.name, self.value_type)

    class Meta:
        app_label = 'tracking'


class SiteTracker(BaseModel):

    tracker = models.ForeignKey(Tracker)

    update_date = models.DateTimeField(
         verbose_name='Start Date/Time',
         null=True
        )

    app_name = models.CharField(
        max_length=100,
        )

    model = models.CharField(
        max_length=150,
        )

    tracked_value = models.IntegerField(
        default=0,
        editable=True,
    )

    site_name = models.CharField(
        max_length=200,
        )

    start_date = models.DateTimeField(
         verbose_name='Start Date/Time',
         null=True
        )

    end_date = models.DateTimeField(
        verbose_name='End Date/Time',
        null=True
        )

    def __unicode__(self):
        return "{}_{}".format(self.model, self.tracker.value_type)

    class Meta:
        app_label = 'tracking'
        unique_together = (('site_name', 'tracker'),)
