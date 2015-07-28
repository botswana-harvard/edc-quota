from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import BasicAuthentication
from edc_tracker.models import Tracker


class TrackerResource(ModelResource):

    class Meta:
        resource_name = 'tracker'
        queryset = Tracker.objects.all()
        authenticate = BasicAuthentication()
        authorization = DjangoAuthorization()
