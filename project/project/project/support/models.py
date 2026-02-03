from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils import timezone

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets') #Users only
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"

    def close_ticket(self):
        if self.status != 'closed':
            self.status = 'closed'
            self.save()

    def set_in_progress(self):
        if self.status != 'in_progress':
            self.status = 'in_progress'
            self.save()

    def reopen_ticket(self):
        if self.status != 'open':
            self.status = 'open'
            self.save()

    def delete_ticket(self):
        self.replies.all().delete()
        self.delete()

    def get_latest_reply(self):
        return self.replies.order_by('created_at').first()

    def is_open(self):
        return self.status == 'open'

    def is_in_progress(self):
        return self.status == 'in_progress'

    def is_closed(self):
        return self.status == 'closed'

    def time_since_creation(self):
        delta = timezone.now() - self.created_at
        return delta

class TicketReply(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE) #Users or Tech
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.user.username} on Ticket #{self.ticket.id}"

    def delete_reply(self):
        self.delete()

    def is_latest_reply(self):
        return self == self.ticket.replies.order_by('created_at').first()

    def time_since_creation(self):
        delta = timezone.now() - self.created_at
        return delta
