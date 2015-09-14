import os
from django.apps import apps
from django.contrib.auth.models import make_password, Group, Permission, User
from tastypie.models import ApiKey


class Configure:

    def __init__(self, username=None, groupname=None, email=None, shared_apikey=None):
        self.app_label = 'edc_quota'
        self.username = username or 'edc_quota'
        self.groupname = groupname or 'edc_quota_api'
        self.email = 'django@example.com'
        self.shared_apikey = shared_apikey
        try:
            self.user = User.objects.get(username=self.username)
        except User.DoesNotExist:
            password = str(os.urandom(4))
            self.user = User.objects.create(
                username=self.username,
                password=make_password(password),
                email=self.email)
        try:
            self.group = Group.objects.get(name=self.groupname)
        except Group.DoesNotExist:
            self.group = Group.objects.create(name=self.groupname)
        for permission in Permission.objects.filter(
                content_type__app_label=self.app_label).exclude(codename__startswith='delete'):
            self.group.permissions.add(permission)
        self.user.groups.add(self.group)
        if self.shared_apikey:
            apikey = ApiKey.objects.get(user=self.user)
            apikey.key = self.shared_apikey
            apikey.save()
        self.quotas_created = self.create_quotas()

    @property
    def apikey(self):
        try:
            return ApiKey.objects.get(user=self.user).key
        except ApiKey.DoesNotExist:
            return None

    def create_initial_quota(self, model_cls):
        """Attempts to create an initial quota if the model has set the attributes
        QUOTA_TARGET, START_DATE, EXPIRATION_DATE."""
        try:
            if not model_cls.quota.get_quota():
                model_cls.quota.set_quota(
                    target=model_cls.QUOTA_TARGET,
                    start_date=model_cls.START_DATE,
                    expiration_date=model_cls.EXPIRATION_DATE)
        except AttributeError:
            pass

    def create_quotas(self):
        quotas = []
        for app_config in apps.get_app_configs():
            for model_cls in app_config.get_models():
                self.create_initial_quota(model_cls)
        return quotas
