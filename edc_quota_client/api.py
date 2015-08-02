from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import BasicAuthentication
from .models import Quota


class QuotaResource(ModelResource):

    class Meta:
        resource_name = 'quota'
        queryset = Quota.objects.all()
        authenticate = BasicAuthentication()
        authorization = DjangoAuthorization()
