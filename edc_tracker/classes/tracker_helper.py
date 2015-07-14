from datetime import datetime

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from edc.device.device.classes import Device

from ..models import Tracker, SiteTracker
from .mail import Reciever, Mail


class TrackerHelper(object):
    """Calculates and updates tracked value.
    """

    def __init__(self, plot=None, household_structure=None):
        """Sets value_type, and tracker server name."""

        self.value_type = None
        self.central_server_name = settings.TRACKER_SERVER_NAME
        self.tracked_model = None

    def update_site_tracker(self):
        """Update the tracker and site tracker at the site."""

        online_sites = self.online_producers
        if Device().is_central_server:
            for site in self.registered_sites:
                # Update tracker
                using = site + ".bhp.org.bw"
                if using in online_sites:
                    try:
                        tracker = Tracker.objects.get(
                            is_active=True,
                            central_server_name=self.central_server_name,
                            value_type=self.value_type
                        )
                        tracker.save(
                            update_fields=['tracked_value', 'update_date'],
                            using=using
                        )
                    except Tracker.DoesNotExist:
                        # Create the tracker if it does not exist.
                        Tracker.objects.using(using).create(
                            is_active=True,
                            central_server_name=self.central_server_name,
                            value_type=self.value_type,
                            app_name='',
                            model='',
                            tracked_value=self.central_tracked_value,
                            start_date=datetime.today(),
                            end_date=datetime.today()
                        )

                    # Update site tracker
                    try:
                        site_tracker = SiteTracker.objects.get(site_name=site)
                        site_tracker.tracked_value = self.site_tracked_value(
                            site
                        )
                        site_tracker.update_date = datetime.today()
                        site_tracker.save(
                            update_fields=['tracked_value', 'update_date'],
                            using=using
                        )
                    except SiteTracker.DoesNotExist:
                        # Create the site tracker if it does not exist.
                        SiteTracker.objects.using(using).create(
                            is_active=True,
                            tracker=tracker,
                            central_server_name=self.central_server_name,
                            value_type=self.value_type,
                            app_name='bcpp_subject',
                            site_name=site,
                            model='PimaVl',
                            tracked_value=self.site_tracked_value(site),
                            start_date=datetime.today(),
                            end_date=datetime.today()
                        )

    def update_producer_tracker(self):
        """Updates the tracked value on the producer.

        Attributes:
        using: The using value for the database in the producer.
        value_type: The type of value being tracked, e.g mobile setup or household setup for poc vl.
        central_server_name: The name of the central site
        """

        site = settings.CURRENT_COMMUNITY
        online_sites = self.online_producers
        if Device().is_community_server:
            for using in online_sites:
                if not using in settings.MIDDLE_MAN_LIST:
                    # Update tracker
                    try:
                        tracker = Tracker.objects.get(
                            is_active=True,
                            central_server_name=self.central_server_name,
                            value_type=self.value_type
                        )
                        tracker.save(
                            update_fields=['tracked_value', 'update_date'],
                            using=using
                        )
                    except Tracker.DoesNotExist:
                        # Create the tracker if it does not exist.
                        Tracker.objects.using(using).create(
                            is_active=True,
                            central_server_name=self.central_server_name,
                            value_type=self.value_type,
                            app_name='',
                            model='',
                            tracked_value=self.site_tracked_value(site),
                            start_date=datetime.today(),
                            end_date=datetime.today()
                        )
                    # Update site tracker
                    try:
                        site_tracker = SiteTracker.objects.get(site_name=site)
                        site_tracker.tracked_value = self.site_tracked_value(site)
                        site_tracker.update_date = datetime.today()
                        site_tracker.save(
                            update_fields=['tracked_value', 'update_date'], 
                            using=using
                        )
                    except SiteTracker.DoesNotExist:
                        # Create the site tracker if it does not exist.
                        SiteTracker.objects.using(using).create(
                            is_active=True,
                            tracker=tracker,
                            central_server_name=self.central_server_name,
                            value_type=self.value_type,
                            app_name='bcpp_subject',
                            site_name=site,
                            model='PimaVl',
                            tracked_value=self.site_tracked_value(site),
                            start_date=datetime.today(),
                            end_date=datetime.today()
                        )

    def update_central_tracker(self, using='default'):
        """Undates the tracked value on the central site."""

        if Device().is_central_server:
            try:
                tracker = Tracker.objects.get(
                    is_active=True,
                    central_server_name=self.central_server_name,
                    value_type=self.value_type
                )
                tracker.tracked_value = self.central_tracked_value
                tracker.update_date = datetime.today()
                tracker.save(update_fields=['tracked_value', 'update_date'])
            except Tracker.DoesNotExist:
                Tracker.objects.create(
                    is_active=True,
                    central_server_name=self.central_server_name,
                    value_type=self.value_type,
                    app_name='bcpp_subject',
                    model='PimaVl',
                    tracked_value=self.central_tracked_value,
                    start_date=datetime.today(),
                    end_date=datetime.today()
                )
            for site in self.registered_sites:
                try:
                    site_tracker = SiteTracker.objects.get(site_name=site)
                    site_tracker.tracked_value = self.site_tracked_value(site)
                    site_tracker.update_date = datetime.today()
                    site_tracker.save(
                        update_fields=['tracked_value', 'update_date']
                    )
                except SiteTracker.DoesNotExist:
                    SiteTracker.objects.create(
                        is_active=True,
                        tracker=tracker,
                        central_server_name=self.central_server_name,
                        value_type=self.value_type,
                        app_name='bcpp_subject',
                        site_name=site,
                        model='PimaVl',
                        tracked_value=self.tracked_value,
                        start_date=datetime.today(),
                        end_date=datetime.today()
                    )

    @property
    def tracked_value(self):
        """Gets the tracked value."""
        try:
            return Tracker.objects.get(
                        value_type=self.value_type,
                        central_server_name=self.central_server_name,
                        is_active=True).tracked_value
        except Tracker.DoesNotExist:
            raise ImproperlyConfigured(
                    'Cannot retrieve tracker model instance,'
                    'make sure it exists.'
                  )

    @property
    def central_tracked_value(self):
        """Counts all Tracked values from all sites."""
        tracked_value = self.tracked_model.objects.filter(
            value_type=self.value_type,
            ).count()
        return tracked_value

    @property
    def tracker(self):
        """Gets the tracker instance."""
        try:
            return Tracker.objects.get(
                       value_type=self.value_type,
                       central_server_name=self.central_server_name,
                       is_active=True
                    )
        except Tracker.DoesNotExist:
            raise ImproperlyConfigured(
                        'Cannot retrieve tracker model instance,'
                        'make sure it exists.'
                    )

    @property
    def tracker_limit(self):
        """ Return the limit balance."""
        return self.tracker.value_limit - self.tracked_value

    def site_tracked_value(self, site, using='default'):
        """Gets the value of the tracked value for the site."""
        site_tracked_value = self.tracked_model.objects.using(using).filter(
            value_type=self.value_type,
            site_name=site
            )
        site_tracked_value.count()
        return site_tracked_value

    @property
    def registered_sites(self):
        return settings.REGISTERED_SITES

    @property
    def update_trackers(self):
        """Update all trackers."""

        self.update_site_tracker()
        self.update_producer_tracker()
        self.update_central_tracker()

    def tracked_values(self):
        tracked_dict = {}
        color_scheme = ['F2FFA1', 'FFE787', 'FF9A42', 'FF4B1F']
        if self.tracked_value == 400:
            req_color = color_scheme[3]
        elif self.tracked_value >= 390:
            req_color = color_scheme[2]
        elif self.tracked_value >= 350:
            req_color = color_scheme[1]
        else:
            req_color = color_scheme[0]
        tracked_dict['tracked_value'] = self.tracked_value
        tracked_dict['value_type'] = TrackerHelper().value_type
        tracked_dict['req_pimavl'] = TrackerHelper().required_pimavl
        tracked_dict['color_status'] = req_color
        return tracked_dict

    def send_email_notification(self):
        if Device().is_central_server:
            if self.tracked_value >= 300:
                mail = Mail(receiver=Reciever())
                mail.send_mail_with_cc_or_bcc()
