[![Build Status](https://travis-ci.org/botswana-harvard/edc-quota.svg?branch=develop)](https://travis-ci.org/botswana-harvard/edc-quota)

[![Coverage Status](https://coveralls.io/repos/botswana-harvard/edc-quota/badge.svg?branch=develop&service=github)](https://coveralls.io/github/botswana-harvard/edc-quota?branch=develop)

# edc-quota

Keep track of the number of instances created for a specified model on one or more offline clients managed by a central controller.

Clients are disconnected from the central controller when collecting data. They go online at the end of each shift or day
and are contacted by the controller.

- sets an overall quota for a model managed by a central controller
- sets a quota per client model to be managed by the client
- central controller can change the quota per registered client over REST API
- central controller can update itself on progress of all clients toward reaching the over overall quota
- central controller can approve for a client to override it's quota.
 
There are two apps, `edc_quota_controller` and `edc_quota_client`.

`edc_quota_controller` is only needed if you have offline clients collecting "model instances" toward an overall quota.

edc_quota_client
----------------

`edc_quota_client` can expose a REST API to query progress towards a quota. Add this to your `urls.py` if you want OR if you are using `edc_quota_controller`.

	from tastypie.api import Api
	from edc_quota_client.api import QuotaResource

	api = Api(api_name='v1')
	api.register(QuotaResource())

	urlpatterns += [url(r'^api/', include(api.urls))]


Declare your model with the `QuotaMixin`:

	from edc_quota_client.models import QuotaMixin 

	class MyModel(QuotaMixin, models.Model):
	
		field1 = models.CharField(max_length=25)

		field2 = models.CharField(max_length=25)
		
		class Meta:
			app_label = 'my_app'
			
Set a quota:
	
	from datetime import timedelta
	from django.utils import timezone
	from edc_quota_client.models import Quota
	
	Quota.objects.create(
		app_label=MyModel._meta.app_label,
		model_name=MyModel._meta.object_name,
		expires_datetime=timezone.now() + timedelta(days=1),
		target=100
	)
		
Model will raise an exception before more than 100 instances are created  

	>>> for _ in range(0, 100):
	>>> 	MyModel.objects.create()
	>>>	
	>>> MyModel.objects.create()
	QuotaReachedError: Quota for model MyModel has been reached.
	
Check progress toward the quota:

	>>> quota = Quota.objects.filter(
			app_label=MyModel._meta.app_label,
			model_name=MyModel._meta.object_name,
		).latest()
	>>> quota.target
	100
	>>> quota.model_count
	100
	
edc_quota_controller
--------------------

The controller `get`s model_counts from each registered client, calculates a new quota targets, and `put` updated quota targets to each client.

Models involved are in `edc_quota_controller`: `quota` `quota_history` and `client`.

The controller will register all clients associated with a defined `quota`. The association is on `app_label` and `model_name`.

    For example:

        quota = Quota.objects.get(...)

        controller = Controller(quota)
        controller.get_all()
        controller.post_all()

Recall with `edc_quota_client` a `quota` refers to a target count expected for a particular model. Unlike a `Quota` on the clients, `edc_quota_controller.Quota` on the controller does not refer to an models on the controller. Model `Quota` on the controller is a reference model of quotas that the controller manages for its clients. There is one quota instance per quota managed.

Model `edc_quota_controller.quota_history` is added to each time the controller updates the quota on its clients.
 
