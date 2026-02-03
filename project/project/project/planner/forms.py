from django.forms import ModelForm, DateInput
from planner.models import Event, EventMember
from django import forms


class EventForm(ModelForm):
    """ Form for adding new events """

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields["start_time"].input_formats = ('%Y-%m-%dT%H:%M',)
        self.fields["end_time"].input_formats = ('%Y-%m-%dT%H:%M',)

    def clean(self):
        cleaned_data = super().clean()
        
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time > end_time:
            self.add_error('end_time', "End time cannot be earlier than start time!")
        return cleaned_data
    
    class Meta:
        model = Event
        fields = ["title", "description", "start_time", "end_time"]
        #https://docs.djangoproject.com/en/5.1/ref/forms/widgets/
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter event title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "placeholder": "Enter event description",}), #just larger version of TextInput
            "start_time": DateInput(attrs={"type": "datetime-local", "class": "form-control"}, format='%Y-%m-%dT%H:%M',),
            "end_time": DateInput(attrs={"type": "datetime-local", "class": "form-control"}, format='%Y-%m-%dT%H:%M',),
        }
        exclude = ["user"] # should be added by AddMemberForm

class AddMemberForm(forms.ModelForm):
    """ Form for adding new users to event by id """

    class Meta:
        model = EventMember
        fields = ["user"]

class DeleteMemberForm(forms.Form):
    """ Form for deletting new users from event by id """

    member = forms.ModelChoiceField(queryset=EventMember.objects.none(), label="Select Member")

    def __init__(self, *args, **kwargs):
        event_id = kwargs.pop('event_id', None)
        super().__init__(*args, **kwargs)
        if event_id:
            self.fields['member'].queryset = EventMember.objects.filter(event_id=event_id)