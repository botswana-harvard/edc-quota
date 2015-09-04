from datetime import date
from collections import namedtuple
try:
    from django.apps.apps import get_model
except ImportError:
    from django.db.models import get_model
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

from ..override import Override, OverrideError

from .exceptions import QuotaReachedError

QuotaTuple = namedtuple('QuotaTuple', 'target model_count expiration_date pk reached expired')


class Quota(models.Model):
    """Client's local quota reference model.

    Quota model is updated by the controller."""

    get_latest_by = "quota_datetime"

    app_label = models.CharField(max_length=25)

    model_name = models.CharField(max_length=25)

    model_count = models.IntegerField(default=0)

    target = models.IntegerField()

    expiration_date = models.DateField()

    is_active = models.BooleanField(default=True)

    quota_datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{}(target={})".format(self.model_name, self.target)

    class Meta:
        app_label = 'edc_quota'


class QuotaManager(models.Manager):

    """A manager for a model that uses the QuotaMixin."""

    def set_quota(self, target, expiration_date):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.object_name
        model_count = get_model(app_label, model_name).objects.all().count()
        Quota.objects.create(
            app_label=app_label,
            model_name=model_name,
            model_count=model_count,
            target=target,
            expiration_date=expiration_date
        )

    def get_quota(self):
        quota = Quota.objects.filter(
            app_label=self.model._meta.app_label,
            model_name=self.model._meta.object_name,
        ).order_by('quota_datetime').last()
        try:
            reached = True if (quota.target <= quota.model_count) else False
            expired = True if date.today() > quota.expiration_date else False
            return QuotaTuple(quota.target, quota.model_count, quota.expiration_date, quota.pk, reached, expired)
        except AttributeError:
            return QuotaTuple(None, None, None, None, None, None)

    @property
    def quota_reached(self):
        quota = self.get_quota()
        if quota.reached:
            return True
        elif quota.expired:
            return True
        return False

    @property
    def quota_expired(self):
        return self.get_quota().expired


class QuotaMixin(object):

    err_message = None

    quota_pk = models.CharField(max_length=36, null=True)

    def save(self, *args, **kwargs):
        if self.quota_reached:
            raise QuotaReachedError(self.err_message)
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
        try:
            quota = Quota.objects.filter(
                app_label=self._meta.app_label,
                model_name=self._meta.object_name,
            ).last()
            reached = self.__class__.objects.quota_reached
            expired = self.__class__.objects.quota_expired
            if expired and reached:
                self.err_message = 'Quota for model {} has expired.'.format(self.__class__.__name__)
                quota_reached = True
            elif reached:
                self.err_message = 'Quota for model {} has been reached.'.format(self.__class__.__name__)
                quota_reached = True
            else:
                quota_reached = False
            self.quota_pk = quota.pk
        except Quota.DoesNotExist:
            quota_reached = False
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
