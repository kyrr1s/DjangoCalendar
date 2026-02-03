from django.urls import path
from planner import views

app_name = "planner"

urlpatterns = [
    path('', views.index, name='index'), 

    path("planner/", views.Planner.as_view(), name="planner"),

    path('next_week/<int:event_id>/', views.next_week, name='next_week'),
    path('next_day/<int:event_id>/', views.next_day, name='next_day'),

    path("event/new/", views.create_event, name="event_new"),
    path("event/edit/<int:pk>/", views.EventEdit.as_view(), name="event_edit"),
    path('delete-event/<int:pk>/', views.EventDelete.as_view(), name='delete_event'),

    path("add-event-member/<int:event_id>", views.eventmember_add, name="eventmember_add"),
    path("delete-event-member/<int:event_id>/<int:member_id>/", views.EventMemberDelete.as_view(), name="eventmember_delete"),
    
    path("events/", views.AllEventsList.as_view(), name="all_events"),
    path("running-events/",views.RunningEventsList.as_view(),name="running_events",),
    path("upcoming-events/", views.UpcomingEventsList.as_view(), name="upcoming_events",),
    path("completed-events/", views.CompletedEventsList.as_view(),name="completed_events",),
]