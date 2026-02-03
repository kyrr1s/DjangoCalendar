from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Event, EventMember
from .forms import EventForm, AddMemberForm
from .models import Event, EventMember

class EventModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.event = Event.objects.create(
            user=self.user,
            title="Test Event",
            description="Test Event Description",
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=2)
        )

    def test_event_creation(self):
        self.assertEqual(self.event.title, "Test Event")
        self.assertEqual(self.event.description, "Test Event Description")
        self.assertTrue(self.event.is_active)

    def test_get_html_url(self):
        expected_url = f'<a href="/event/edit/{self.event.id}/"> Test Event </a>'
        self.assertEqual(self.event.get_html_url, expected_url)

    def test_event_member_creation(self):
        event_member = EventMember.objects.create(event=self.event, user=self.user)
        self.assertEqual(str(event_member), self.user.username)

class EventManagerTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.event1 = Event.objects.create(user=self.user1, title="Event1", description="Desc", start_time=timezone.now(), end_time=timezone.now() + timezone.timedelta(hours=1))
        self.event2 = Event.objects.create(user=self.user2, title="Event2", description="Desc", start_time=timezone.now(), end_time=timezone.now() + timezone.timedelta(hours=1))
        EventMember.objects.create(event=self.event2, user=self.user1)

    def test_get_all_events(self):
        # user1 is the creator of event1 and a member of event2
        events_user1 = Event.objects.get_all_events(user=self.user1)
        self.assertIn(self.event1, events_user1)
        self.assertIn(self.event2, events_user1)

        # user2 is the creator of event2 but not part of event1
        events_user2 = Event.objects.get_all_events(user=self.user2)
        self.assertNotIn(self.event1, events_user2)
        self.assertIn(self.event2, events_user2)

############################## FORMS TESTS ########################

class EventFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_valid_event_form(self):
        data = {
            'title': "Test Event",
            'description': "Test Description",
            'start_time': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'end_time': (timezone.now() + timezone.timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M')
        }
        form = EventForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_event_form_due_end_time(self):
        data = {
            'title': "Test Event",
            'description': "Test Description",
            'start_time': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'end_time': timezone.now().strftime('%Y-%m-%dT%H:%M')
        }
        form = EventForm(data=data)
        self.assertEqual(form.errors['end_time'], ["End time cannot be earlier than start time!"])

class AddMemberFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.event = Event.objects.create(user=self.user, title="Test Event", description="Test", start_time=timezone.now(), end_time=timezone.now() + timezone.timedelta(hours=1))

    def test_add_member_form(self):
        # Assuming queryset was passed correctly
        form = AddMemberForm(data={'user': self.user.id})
        self.assertTrue(form.is_valid())