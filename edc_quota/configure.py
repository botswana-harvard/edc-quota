import os
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

    @property
    def apikey(self):
        try:
            return ApiKey.objects.get(user=self.user).key
        except ApiKey.DoesNotExist:
            return None
