from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from edc_quota import Override, OverrideError

from .exceptions import QuotaReachedError


class Quota(models.Model):
    """Client's local quota reference model.

    Quota model is updated by the controller."""

    get_latest_by = "quota_datetime"

    app_label = models.CharField(max_length=25)

    model_name = models.CharField(max_length=25)

    model_count = models.IntegerField(default=0)

    target = models.IntegerField()

    expires_datetime = models.DateTimeField()

    is_active = models.BooleanField(default=True)

    quota_datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{}".format(self.model_name)

    class Meta:
        app_label = 'edc_quota_client'


class QuotaMixin(object):

    quota_pk = models.CharField(max_length=36, null=True)

    def save(self, *args, **kwargs):
        if self.quota_reached:
            raise QuotaReachedError(
                'Quota for model {} has been reached.'.format(self.__class__.__name__))
        super(QuotaMixin, self).save(*args, **kwargs)

    @property
    def quota_reached(self):
        """Returns True if the model instance count is greater than the quota target for this model.

        - called from the save method;
        - ignores existing instances;
        - will raise an exception if no Quota for this model.
        """
        if self.id:
            return False
        quota = Quota.objects.filter(
            app_label=self._meta.app_label,
            model_name=self._meta.object_name,
        ).last()
        if quota.expires_datetime > timezone.now():
            quota_reached = quota.model_count >= quota.target
        else:
            quota_reached = True
        self.quota_pk = quota.pk
        return quota_reached


class QuotaModelWithOverride(QuotaMixin, models.Model):

    override_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
    )

    confirmation_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):
        if self.quota_reached:
            try:
                self.override_quota()
            except OverrideError as err:
                raise QuotaReachedError(
                    'Quota for model {} has been reached. Got {}'.format(
                        self.__class__.__name__, str(err)))
        super(QuotaMixin, self).save(*args, **kwargs)

    def override_quota(self, exception_cls=None):
        exception_cls = exception_cls or OverrideError
        override = Override(self.override_code, self.confirmation_code)
        if not override.is_valid_combination:
            raise exception_cls(
                'Invalid code combination. Got {} and {}'.format(override.code, override.confirmation_code))
        return None

    class Meta:
        abstract = True


@receiver(post_save, weak=False, dispatch_uid="quota_on_post_save")
def quota_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Increments the quota or passes on an AttributeError."""
    if not raw:
        if created:
            try:
                quota = Quota.objects.get(pk=instance.quota_pk)
                quota.model_count += 1
                quota.save()
            except AttributeError:
                pass
