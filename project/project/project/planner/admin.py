from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Event, EventMember

class EventResource(resources.ModelResource):
    class Meta:
        model = Event
        fields = '__all__'

class EventMemberResource(resources.ModelResource):
    class Meta:
        model = EventMember
        fields = '__all__' 

@admin.register(Event)
class EventAdmin(ImportExportModelAdmin):
    resource_class = EventResource
    list_display = [field.name for field in Event._meta.fields]
    search_fields = [field.name for field in Event._meta.fields]
    list_filter = [field.name for field in Event._meta.fields if field.get_internal_type() not in ['TextField']]

@admin.register(EventMember)
class EventMemberAdmin(ImportExportModelAdmin):
    resource_class = EventMemberResource
    list_display = [field.name for field in EventMember._meta.fields]
    search_fields = [field.name for field in EventMember._meta.fields]
    list_filter = [field.name for field in EventMember._meta.fields if field.get_internal_type() not in ['TextField']]