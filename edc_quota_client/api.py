from tastypie.resources import ModelResource
from tastypie.authorization import ReadOnlyAuthorization, DjangoAuthorization
from tastypie.authentication import Authentication, BasicAuthentication
from .models import Quota


class QuotaResource(ModelResource):

    class Meta:
        resource_name = 'quota'
        queryset = Quota.objects.all()
        fields = ['target', 'model_count', 'id', 'quota_datetime', 'app_label', 'model_name']
        allowed_methods = ['get', 'post', 'put']
        filtering = {
            'app_label': ['exact'],
            'model_name': ['iexact'],
        }
        authentication = BasicAuthentication()
