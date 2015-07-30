from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import BasicAuthentication
from edc_quota_monitor.models import MasterQuota, ClientQuota


class MasterQuotaResource(ModelResource):

    class Meta:
        resource_name = 'master_quota'
        queryset = MasterQuota.objects.all()
        authenticate = BasicAuthentication()
        authorization = DjangoAuthorization()


class ClientQuotaResource(ModelResource):

    class Meta:
        resource_name = 'client_quota'
        queryset = ClientQuota.objects.all()
        authenticate = BasicAuthentication()
        authorization = DjangoAuthorization()
