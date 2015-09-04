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
 
Installation
------------

Add the `edc_quota` app to your project `settings`:

	INSTALLED_APPS = (
	...
	'edc_quota', 
	...
	)

Include the `edc_quota` urls in your project `urls`:

	urlpatterns += patterns('edc_quota', url(r'^edc_quota/', include('edc_quota.urls')))


Usage
-----

Declare your model with the `QuotaMixin` and the `QuotaManager`:

	from edc_quota.client import QuotaMixin, QuotaManager

	class MyModel(QuotaMixin, models.Model):
	
		field1 = models.CharField(max_length=25)

		field2 = models.CharField(max_length=25)

		objects = QuotaManager()
		
		class Meta:
			app_label = 'my_app'
			
Set a quota:
	
	from datetime import date, timedelta
	
	MyModel.objects.set_quota(
	    expiration_date=date.today() + timedelta(days=1),
		target=100
	)

Use your model:
	>>> for _ in range(0, 25):
	>>> 	MyModel.objects.create()

Check progress toward the quota:
	>>> target, model_count, expiration_date = MyModel.objects.get_quota()
	>>> target
	100
	>>> model_count
	25

Once the target is reached, your Model will raise an exception before more than 100 instances are created  

	>>> MyModel.objects.all().count()
	25
	>>> for _ in range(0, 75):
	>>> 	MyModel.objects.create()
	>>> MyModel.objects.all().count()
	100
	>>> MyModel.objects.create()
	QuotaReachedError: Quota for model MyModel has been reached.
	

Using with the Controller
-------------------------

The controller gets model_counts (`get`) from each registered client, calculates new quota targets, and updates quota targets (`put`) to each client. It manages one quota instance per controller instance.

Models involved are in `edc_quota.controller`: `ControllerQuota` `QuotaHistory` and `Client`.

The controller registers all clients associated with the `ControllerQuota`. The association is on `app_label` and `model_name`.

    For example:

        quota = Quota.objects.get(...)

        controller = Controller(quota)
        controller.get_all()
        controller.post_all()

Recall with `edc_quota.client` a `quota` refers to a target count expected for a particular model. Unlike a `Quota` on the clients, `ControllerQuota` on the controller does NOT refer to any models on the controller. `ControllerQuota` on the controller is a reference model of quotas that the controller manages for its clients. There is one quota instance on the controller per client quota managed.

A new instance is added to model `edc_quota.controller.quota_history` for each client quota updated by the controller.
 
The `Controller` accepts either an instance of `ControllerQuota` or the `app_label` and `model_name` needed to get the `ControllerQuota` instance. The `Controller` will raise a `ControllerQuota.DoesNotExist` error if the quota model instance is not active, expired, or does not exist.

To get/post to a single client or a select list of clients, pass a list of client hostnames to the Controller:
 
    controller = Controller(quota, clients=['host1', 'host2'])
    controller.get_all()
    controller.post_all()
 
