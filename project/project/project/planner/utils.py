from calendar import HTMLCalendar
from datetime import datetime
from planner.models import Event, EventMember
from django.db.models import Q

def get_date(req_day=None):
    """ Recieve current date or date of the first day in a month in format MM-YYYY """
    if req_day:
        return datetime.strptime(req_day, "%m-%Y").date()
    return datetime.today().replace(day=1)


def prev_month(date):
    """ Receieve str with prev month in format MM-YYYY """
    year, month = (date.year, date.month - 1) if date.month > 1 else (date.year - 1, 12)
    return f"month={month:02}-{year}"


def next_month(date):
    """ Receieve str with next month in format MM-YYYY """
    year, month = (date.year, date.month + 1) if date.month < 12 else (date.year + 1, 1)
    return f"month={month:02}-{year}"

class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None, user=None):
        self.year = year
        self.month = month
        self.user = user
        super(Calendar, self).__init__()

    def formatday(self, day, events):
        events_per_day = events.filter(start_time__day=day)
        date = ""
        for event in events_per_day:
            date += f'<li> {event.get_html_url} </li>'
        if day != 0:
            return f"<td><span class='date'>{day}</span><ul> {date} </ul></td>"
        return "<td></td>"

    def formatweek(self, theweek, events):
        week = ""
        for d, _ in theweek:
            week += self.formatday(d, events)
        return f"<tr>{week}</tr>"

    def formatmonth(self, withyear=True):
        # Корректное использование обратного отношения через related_name
        events = Event.objects.filter(
            start_time__year=self.year, 
            start_time__month=self.month
        ).filter(
            Q(user=self.user) | Q(members__user=self.user)
        ).distinct()

        cal = ('<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n')
        cal += (f"{self.formatmonthname(self.year, self.month, withyear=withyear)}\n")
        cal += f"{self.formatweekheader()}\n"
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f"{self.formatweek(week, events)}\n"
        return cal