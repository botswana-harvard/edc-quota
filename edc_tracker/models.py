from django.db import models


class Tracker(models.Model):

    update_date = models.DateTimeField(
        verbose_name='Start Date/Time',
        null=True
    )

    is_active = models.BooleanField(
        default=True,
        help_text=("Is the tracker active."))

    master_server_url = models.CharField(
        max_length=100,
        help_text=("The url of the central server, e.g central.bhp.org.bw.")
    )

    value_type = models.CharField(
        max_length=100,
        help_text=("Type of the value being tracked.")
    )

    app_name = models.CharField(
        max_length=100,
        help_text=("App name of the value being tracked.")
    )

    model_name = models.CharField(
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

    def __str__(self):
        return "{}_{}".format(self.master_server_url, self.value_type)

    class Meta:
        app_label = 'edc_tracker'


class SiteTracker(models.Model):

    tracker = models.ForeignKey(Tracker)

    update_date = models.DateTimeField(
        verbose_name='Start Date/Time',
        null=True
    )

    app_name = models.CharField(
        max_length=100,
    )

    model_name = models.CharField(
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

    def __str__(self):
        return "{}_{}".format(self.model_name, self.tracker.value_type)

    class Meta:
        app_label = 'edc_tracker'
        unique_together = (('site_name', 'tracker'),)
