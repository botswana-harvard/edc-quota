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


If you want a link to the Override form from the model, override the admin change_form template for the model. In the tests, the `TestQuotaModel` change_form is placed in `templates/admin/edc_quota/testquotamodel`. See the [django docs](https://docs.djangoproject.com/en/1.8/ref/contrib/admin/#templates-which-may-be-overridden-per-app-or-model "templates-which-may-be-overridden-per-app-or-model") for more information.

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
	
	MyModel.objects.set_quota(100, date.today() + timedelta(days=1))

Use your model:

	>>> for _ in range(0, 25):
	>>> 	MyModel.objects.create()

Check progress toward the quota:

	>>> quota = MyModel.objects.get_quota()
	>>> quota.target
	100
	>>> quota.model_count
	25
	>>> quota.reached
	False

Once the target is reached, your Model will raise an exception before more than 100 instances are created  

	>>> MyModel.objects.all().count()
	25
	>>> for _ in range(0, 75):
	>>> 	MyModel.objects.create()
	>>> MyModel.objects.all().count()
	100
	>>> MyModel.objects.quota_reached
	True
	>>> MyModel.objects.create()
	QuotaReachedError: Quota for model MyModel has been reached.
	

Manager methods
---------------

`Model.objects.set_quota(target, expiration_date)`:

Sets a quota. If model instances already exist, the model_count attribute will be updated with the count. 
	
`Model.objects.get_quota()`

Returns a namedtuple with attributes `target, model_count, expiration_date, pk, reached, expired`.

`Model.objects.quota_reached` (property):

Returns True if the target has been met or the quota is expired.

`Model.objects.quota_expired` (property):

Returns True if the quota is expired.


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

Setup Controller and Clients
----------------------------

The REST API (TastyPie) is set to use ApikeyAuthentication. You can use the management command `setupedcquota` to create a special user account, APIKEY and group with add/change permissions. For example:

On the controller:

	>>>python manage.py setupedcquota
	User 'edc_quota' has been created
	User 'edc_quota': added to group 'edc_quota_api'
	User 'edc_quota': apikey b30faa54acd475b9b0d96dd7d9bc54e59856cacc

On each of the clients: (may share the apikey)

	>>>python manage.py setupedcquota b30faa54acd475b9b0d96dd7d9bc54e59856cacc
	User 'edc_quota' has been created
	User 'edc_quota': added to group 'edc_quota_api'
	User 'edc_quota': apikey b30faa54acd475b9b0d96dd7d9bc54e59856cacc

Overriding a Quota
------------------

Once the quota has been reached, a user may bypass the quota one instance at a time using a pair of codes; namely the _override request code_ and the _override code_. In the exception message the user is told the quota has been reached and is shown the _override request code_. The _override request code_ is needed to create an _override code_ on the controller. The codes are entered into the Override model on the client and referenced by the save method of the target model.

Set a quota:

    >>> TestQuotaModel.objects.set_quota(2, date.today())

Reach the quota:

    >>> TestQuotaModel.objects.create()
    >>> TestQuotaModel.objects.create()
    >>> TestQuotaModel.objects.create()
	QuotaReachedError: Quota for model MyModel has been reached.

To try to override, first request an override code:

    >>> test_quota_model = TestQuotaModel()
    >>> test_quota_model.request_code = Code()
    >>> test_quota_model.request_code
	'3UFY9'    

Your supervisor returns an override code based on your request_code

    >>> override_code = Code('3UFY9').validation_code
    >>> override_code
    'NC4GT'

Apply override code and save the model instance:

    >>> test_quota_model.override('NC4GT')
    >>> test_quota_model.save()

Overriding a Quota in Admin
---------------------------

(To be completed)

For a model with a quota, the ModelForm redirects to an interim form that shows the user a request code and presents a form to accept an override code. If a valid override code is entered the interim form will submit and the model is saved. If the user does not have a valid override code, they can cancel and be returned to the model form or some other page, such as a dashboard.

SimpleOverride
--------------

SimpleOverride does not include any models and is the base class for `Override`.

Get an request code:

    >>> from edc_quota import Override
    >>> override = Override()
    >>> request_code = override.request_code
    >>> print(request_code)
    '3UFY9'

Ask for a confirmation code

    >>> from edc_quota import Override
    >>> override = Override(request_code='3UFY9')
    >>> override_code = override.override_code
    >>> print(override_code)
    'NC4GT'

Validate the pair of codes

    >>> from edc_quota import Override
    >>> if Override('3UFY9', 'NC4GT').is_valid_combination:
    >>>>    print('the codes are a valid pair')
 