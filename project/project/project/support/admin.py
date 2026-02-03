from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Ticket, TicketReply

class TicketResource(resources.ModelResource):
    class Meta:
        model = Ticket
        fields = '__all__'

class TicketReplyResource(resources.ModelResource):
    class Meta:
        model = TicketReply
        fields = '__all__'

@admin.register(Ticket)
class TicketAdmin(ImportExportModelAdmin):
    resource_class = TicketResource
    list_display = [field.name for field in Ticket._meta.fields]
    search_fields = [field.name for field in Ticket._meta.fields]
    list_filter = [field.name for field in Ticket._meta.fields if field.get_internal_type() not in ['TextField']]

@admin.register(TicketReply)
class TicketReplyAdmin(ImportExportModelAdmin):
    resource_class = TicketReplyResource
    list_display = [field.name for field in TicketReply._meta.fields]
    search_fields = [field.name for field in TicketReply._meta.fields]
    list_filter = [field.name for field in TicketReply._meta.fields if field.get_internal_type() not in ['TextField']]
