from collections import namedtuple
from datetime import date

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import MinValueValidator
from django.db import models, IntegrityError, transaction

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from ..override.models import OverrideModel
from ..override.override import Override

from .exceptions import QuotaReachedError, QuotaNotSetOrExpiredError

QuotaTuple = namedtuple(
    'QuotaTuple', 'target model_count start_date expiration_date pk target_reached')


class Quota(models.Model):
    """Client's local quota reference model.."""

    get_latest_by = "quota_datetime"

    app_label = models.CharField(max_length=25)

    model_name = models.CharField(max_length=25)

    model_count = models.IntegerField(default=0)

    target = models.IntegerField(
        validators=[MinValueValidator(1)])

    start_date = models.DateField()

    expiration_date = models.DateField()

    is_active = models.BooleanField(default=True)

    quota_datetime = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.model_count = self.model_class().objects.all().count()
        super(Quota, self).save(*args, **kwargs)

    def __str__(self):
        return "{}(target={})".format(self.model_name, self.target)

    def model_class(self):
        try:
            from django.apps import apps
            model_class = apps.get_model(self.app_label, self.model_name)
        except ImportError:
            from django.db.models import get_model
            model_class = get_model(self.app_label, self.model_name)
        return model_class

    class Meta:
        app_label = 'edc_quota'


class QuotaManager(models.Manager):

    """A manager for a model that uses the QuotaMixin."""

    def set_quota(self, target, start_date, expiration_date):
        target = target or 0
        app_label = self.model._meta.app_label
        model_name = self.model._meta.object_name
        model_count = self.model.objects.all().count()
        if start_date > expiration_date:
            raise ValidationError(
                'Quota start date \'{}\' must be less than or equal to the expiration date \'{}\'.'.format(
                    start_date, expiration_date))
        if model_count > target:
            raise QuotaReachedError(
                'Quota cannot be set. A quota of {} has already been met. Got model_count={}.'.format(
                    target or 0, model_count))
        try:
            Quota.objects.get(
                app_label=app_label,
                model_name=model_name,
                target=target,
                start_date=start_date,
                expiration_date=expiration_date,
            )
        except Quota.DoesNotExist:
            with transaction.atomic():
                try:
                    Quota.objects.create(
                        app_label=app_label,
                        model_name=model_name,
                        model_count=model_count,
                        target=target,
                        start_date=start_date,
                        expiration_date=expiration_date,
                    )
                except IntegrityError:
                    pass

    def get_quota(self, report_datetime=None):
        """Returns a quota if it exists for the current period."""
        if report_datetime:
            report_date = report_datetime.date()  # timezone??
        else:
            report_date = date.today()
        try:
            quota = Quota.objects.filter(
                app_label=self.model._meta.app_label,
                model_name=self.model._meta.object_name,
                start_date__lte=report_date,
                expiration_date__gte=report_date).last()
            target_reached = True if (quota.target <= quota.model_count) else False
            return QuotaTuple(
                quota.target, quota.model_count, quota.start_date, quota.expiration_date,
                quota.pk, target_reached)
        except AttributeError:
            pass
        return None

    @property
    def quota_reached(self):
        try:
            if self.get_quota().target_reached:
                return True
        except AttributeError:
            pass
        return False


class QuotaMixin(models.Model):

    QUOTA_TARGET = None
    START_DATE = None
    EXPIRATION_DATE = None
    REPORT_DATETIME_ATTR = 'report_datetime'
    QUOTA_REACHED_MESSAGE = 'Quota for model {} has been reached or exceeded. Got {} >= {}.'

    quota_pk = models.CharField(max_length=36, null=True)

    request_code = models.CharField(max_length=10, null=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            quota = self.__class__.quota.get_quota()
            if not quota:
                if self._meta.proxy:
                    REPORT_DATETIME_ATTR = self._meta.proxy_for_model.REPORT_DATETIME_ATTR
                else:
                    REPORT_DATETIME_ATTR = self.REPORT_DATETIME_ATTR
                raise QuotaNotSetOrExpiredError(
                    'Expected a valid quota for model \'{}\' using {} \'{}\'. Got None.'.format(
                        self.__class__._meta.verbose_name,
                        REPORT_DATETIME_ATTR,
                        getattr(self, REPORT_DATETIME_ATTR).strftime('%Y-%m-%d')))
            try:
                if quota.pk:
                    self.quota_pk = quota.pk
                    if quota.target_reached:
                        try:
                            OverrideModel.objects.get(
                                request_code=self.request_code, instance_pk__isnull=True)
                        except OverrideModel.DoesNotExist:
                            raise QuotaReachedError(
                                self.QUOTA_REACHED_MESSAGE.format(
                                    self.__class__.__name__, quota.model_count, quota.target))
            except AttributeError:
                pass
        super(QuotaMixin, self).save(*args, **kwargs)

    def override(self, override_code):
        Override(instance=self, request_code=self.request_code, override_code=override_code)

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
            except (AttributeError, ObjectDoesNotExist):
                pass
