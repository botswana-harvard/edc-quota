from tastypie.resources import ModelResource
from tastypie.authorization import ReadOnlyAuthorization, DjangoAuthorization
from tastypie.authentication import Authentication, BasicAuthentication
from .models import Quota


class QuotaResource(ModelResource):

    class Meta:
        resource_name = 'quota'
        queryset = Quota.objects.all()
        resource_name = 'subject_consent'
        fields = ['target', 'model_count']
        allowed_methods = ['get']
        filtering = {
            'app_label': ['exact'],
            'model_name': ['iexact'],
        }
        authorization = ReadOnlyAuthorization()
        authentication = Authentication()
