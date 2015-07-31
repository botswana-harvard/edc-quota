from django.contrib import admin

from edc_tracker.forms import SiteTrackerForm, TrackerForm
from edc_tracker.models import Tracker, SiteTracker


class SiteTrackerAdmin(admin.ModelAdmin):
    form = SiteTrackerForm
    fields = (
        'end_date',
        'start_date',
        'tracked_value',
        'site_name',
        'model_name',
        'app_name',
        'update_date',
        'tracker',
        'value_limit'
    )
    list_per_page = 15
    list_display = ('tracked_value', 'site_name', 'update_date', 'tracker')
    list_filter = (
        'end_date',
        'start_date',
        'tracked_value',
        'site_name',
        'update_date'
    )
    search_fields = ['site_name']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "tracker":
            kwargs["queryset"] = Tracker.objects.filter(
                id__exact=request.GET.get('tracker', 0)
            )
        return super(SiteTrackerAdmin, self).formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )

admin.site.register(SiteTracker, SiteTrackerAdmin)


class SiteTrackerInline(admin.TabularInline):
    model = SiteTracker
    extra = 0
    max_num = 5


class TrackerAdmin(admin.ModelAdmin):
    form = TrackerForm
    instructions = []
    inlines = [SiteTrackerInline, ]
    list_per_page = 15
    list_display = (
        'end_date',
        'start_date',
        'tracked_value',
        'master_server_url',
        'model_name',
        'app_name',
        'update_date',
        'value_limit'
    )
    list_filter = ('end_date', 'start_date', 'update_date')
    search_fields = ['name']
admin.site.register(Tracker, TrackerAdmin)
