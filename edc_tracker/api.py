from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import BasicAuthentication
from edc_tracker.models import Tracker


class TrackerResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')

    class Meta:
        resource_name = 'tracker'
        queryset = Tracker.objects.all()
        authenticate = BasicAuthentication()
        authorization = DjangoAuthorization()
