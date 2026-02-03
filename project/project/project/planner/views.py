from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.views.generic import ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from planner.utils import Calendar, get_date, prev_month, next_month
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from datetime import timedelta
from django.utils.safestring import mark_safe
from django.utils.decorators import method_decorator
from datetime import datetime, time
from django.views.decorators.cache import cache_page

from django.views.generic import ListView, UpdateView, DeleteView, View

from planner.models import Event, EventMember

from planner.forms import EventForm, AddMemberForm, DeleteMemberForm

def index(request):
    if request.user.is_authenticated:
        return redirect('planner:planner')
    else:
        return redirect('accounts:login')

#################################### EVENTS #########################################################

# https://docs.djangoproject.com/en/5.1/ref/class-based-views/generic-editing/ <-- ListView handling
class AllEventsList(ListView):
    """ All event list view """

    template_name = "planner/events_list.html"
    model = Event

    def get_queryset(self):
        queryset = Event.objects.get_all_events(user=self.request.user)
        query = self.request.GET.get('search', '')
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset

class RunningEventsList(ListView):
    """ Running events list view """

    template_name = "planner/events_list.html"
    model = Event

    def get_queryset(self):
        queryset = Event.objects.get_running_events(user=self.request.user)
        query = self.request.GET.get('search', '')
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset

class UpcomingEventsList(ListView):
    """ Upcoming events list view """

    template_name = "planner/events_list.html"
    model = Event

    def get_queryset(self):
        queryset = Event.objects.get_upcoming_events(user=self.request.user)
        query = self.request.GET.get('search', '')
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset
    
class CompletedEventsList(ListView):
    """ Completed events list view """

    template_name = "planner/events_list.html"
    model = Event

    def get_queryset(self):
        queryset = Event.objects.get_completed_events(user=self.request.user)
        query = self.request.GET.get('search', '')
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset
    
@login_required
def create_event(request):
    """ View for creating event """
    current_date = datetime.now().date()
    start_time = datetime.combine(current_date, time.min)
    end_time = datetime.combine(current_date, time.max).replace(hour=23, minute=59)

    if request.method == 'POST':
        form = EventForm(request.POST)
        member_form = AddMemberForm(request.POST)
        if form.is_valid() and member_form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            start_time = form.cleaned_data["start_time"]
            end_time = form.cleaned_data["end_time"]
            event = Event.objects.create(
                user=request.user,
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time,
            )
            member_user = member_form.cleaned_data["user"]
            EventMember.objects.create(event=event, user=member_user)
            return redirect("planner:planner")
    else:
        form = EventForm(initial={
            'start_time': start_time.strftime('%Y-%m-%dT%H:%M'),
            'end_time': end_time.strftime('%Y-%m-%dT%H:%M')
        })
        member_form = AddMemberForm()
    
    return render(request, "planner/event_new.html", {"form": form, "member_form": member_form})

# https://docs.djangoproject.com/en/5.1/ref/class-based-views/generic-editing/ <-- UpdateView handling
class EventEdit(UpdateView):
    """ View for updating event box """

    model = Event
    form_class = EventForm
    template_name = "planner/event_edit.html"
    success_url = reverse_lazy("planner:planner")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = Event.objects.get(id=self.object.pk)
        eventmember = EventMember.objects.filter(event=event)
        context.update({
            "event": event,
            "eventmember": eventmember
        })
        return context

# https://docs.djangoproject.com/en/5.1/ref/class-based-views/generic-editing/ <-- DeleteView handling
class EventDelete(DeleteView):
    """ View for deleting an event """
    model = Event
    template_name= "planner/event_delete.html"
    success_url = reverse_lazy('planner:planner') 

############################################## EVENT MEMBERS ##################################33

@login_required()
def eventmember_add(request, event_id):
    """ View for adding users to event by its id """

    event = Event.objects.filter(id=event_id).first()

    error_message = None

    if event is None:
        error_message = "The event does not exist."

    form = AddMemberForm(request.POST or None)
    
    if request.POST and form.is_valid():
        user = form.cleaned_data["user"]
        if not EventMember.objects.filter(event=event, user=user).exists():
            EventMember.objects.create(event=event, user=user)
            return redirect(reverse_lazy('planner:event_edit', args=[event.id]))
        else:
            form.add_error(None, "This user is already a member of the event.")
    
    context = {"form": form, "event": event, "error_message": error_message}
    return render(request, "planner/eventmember_add.html", context)
    
class EventMemberDelete(DeleteView):
    model = EventMember
    template_name = "planner/eventmember_delete.html"

    def get_object(self, queryset=None):
        event_id = self.kwargs['event_id']
        member_id = self.kwargs['member_id']
        return get_object_or_404(EventMember, event_id=event_id, user_id=member_id)

    def get_success_url(self):
        return reverse_lazy('planner:event_edit', args=[self.object.event.id])

#################################### PLANNER ##############################################

@login_required()
def next_week(request, id):
    """ View for creating new event by changing a week in an existing event by id """

    event = get_object_or_404(Event, id=id)
    if request.POST:
        next = event
        next.id = None
        next.start_time += timedelta(days=7)
        next.end_time += timedelta(days=7)
        next.save()
        return JsonResponse({'message': 'Sucessfully change to next week!'})
    else:
        return JsonResponse({'message': 'Error!'}, status=400)

@login_required()
def next_day(request, id):
    """ View for creating new event by changing a day in an existing event by id """
    event = get_object_or_404(Event, id=id)
    if request.POST:
        next = event
        next.id = None
        next.start_time += timedelta(days=1)
        next.end_time += timedelta(days=1)
        next.save()
        return JsonResponse({'message': 'Sucessfully change to next day!'})
    else:
        return JsonResponse({'message': 'Error!'}, status=400)

@method_decorator(cache_page(60 * 5), name='dispatch')   #5min cache 
class Planner(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'planner/planner.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month, self.request.user)
        html_cal = cal.formatmonth(withyear=True)
        context['planner'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context