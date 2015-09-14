from tastypie.resources import ModelResource
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization

from .models import Quota


class QuotaResource(ModelResource):

    class Meta:
        resource_name = 'quota'
        queryset = Quota.objects.all()
        fields = ['target', 'model_count', 'id', 'quota_datetime', 'app_label',
                  'model_name', 'start_date', 'expiration_date']
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put']
        filtering = {
            'app_label': ['exact'],
            'model_name': ['iexact'],
        }
        authorization = Authorization()
        authentication = ApiKeyAuthentication()
