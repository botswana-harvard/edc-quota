"""xx URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.contrib import admin
from django.conf.urls import include
from tastypie.api import Api
from edc_tracker.api import TrackerResource, UserResource


tracker_resource_api = Api(api_name='v1')
tracker_resource_api.register(UserResource())
tracker_resource_api.register(TrackerResource())

urlpatterns = [
    (r'^admin/', include(admin.site.urls)),
    (r'^api/', include(tracker_resource_api.urls))
]
