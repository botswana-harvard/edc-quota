from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.authentication import BasicAuthentication
from .models import Quota


class QuotaResource(ModelResource):

    class Meta:
        resource_name = 'quota'
        queryset = Quota.objects.all()
        fields = [
            'target',
            'model_count',
            'id',
            'quota_datetime',
            'app_label',
            'model_name',
            'expires_datetime'
        ]
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put']
        filtering = {
            'app_label': ['exact'],
            'model_name': ['iexact'],
        }
        authorization = Authorization()
        authentication = BasicAuthentication()
