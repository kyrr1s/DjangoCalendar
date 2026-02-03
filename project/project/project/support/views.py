from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from .models import Ticket, TicketReply
from .forms import TicketCreateForm, TicketReplyForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import send_notification

@login_required
def ticket_list(request):
    tickets = Ticket.objects.filter(user=request.user)
    template = 'support/ticket_list.html'
    error_message = None

    if 'close_ticket' in request.GET:
        ticket_id = request.GET.get('close_ticket')
        ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
        if not ticket.is_closed():
            ticket.close_ticket()
            messages.success(request, f"Ticket #{ticket.id} is closed again.")
        else:
            messages.error(request, f"Ticket #{ticket.id} is already closed.")
    elif 'reopen_ticket' in request.GET:
        ticket_id = request.GET.get('reopen_ticket')
        ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
        if ticket.is_closed():
            ticket.reopen_ticket()
            messages.success(request, f"Ticket #{ticket.id} is opened again.")
        else:
            error_message = f"Ticket #{ticket.id} not closed."

    context = {'tickets': tickets, 'user': request.user, 'error_message': error_message}
    return render(request, template, context)

@login_required
def create_ticket(request):
    template = 'support/create_ticket.html'
    error_message = None

    if request.method == 'POST':
        form = TicketCreateForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()

            send_notification(
                recepient_email="kklimeshov@gmail.com",
                subject="New ticket in your django app!",
                message=f'User {ticket.user.username} created ticket with that text: {ticket.description}'
            )

            messages.success(request, "Ticket is created.")
            return redirect('support:view_ticket', ticket_id=ticket.id)
    else:
        form = TicketCreateForm()

    context = {'form': form, 'user': request.user, 'error_message': error_message}
    return render(request, template, context)


@login_required
def view_ticket(request, ticket_id):
    template = 'support/view_ticket.html'
    error_message = None
    
    if not (request.user.is_superuser or request.user.is_staff):
        ticket = Ticket.objects.filter(id=ticket_id, user=request.user).first()
    else:
        ticket = Ticket.objects.filter(id=ticket_id).first()

    if not ticket:
        error_message = "Ticket does not exist"
        context = {'error_message': error_message}
        return render(request, template, context)

    replies = ticket.replies.all()

    reply_form = None
    if not ticket.is_closed() and request.method == 'POST':
        reply_form = TicketReplyForm(request.POST)
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.user = request.user
            reply.ticket = ticket
            reply.save()
            messages.success(request, "Answer was added.")
            return redirect('support:view_ticket', ticket_id=ticket.id)
    elif not ticket.is_closed():
        reply_form = TicketReplyForm()
        
    context = {'ticket': ticket, 'replies': replies, 'reply_form': reply_form, 'user': request.user, 'error_message': error_message}
    return render(request, template, context)


@login_required
def manage_tickets(request):
    template = 'support/manage_tickets.html'
    error_message = None

    if not (request.user.is_superuser or request.user.is_staff):
        return HttpResponseForbidden("You do not have permission to view this page.")

    tickets = Ticket.objects.all()
    context = {'tickets': tickets, 'user': request.user, 'error_message': error_message}

    if 'close_ticket' in request.GET:
        ticket_id = request.GET.get('close_ticket')
        ticket = get_object_or_404(Ticket, id=ticket_id)
        if not ticket.is_closed():
            ticket.close_ticket()
            messages.success(request, f"Ticket #{ticket.id} is closed.")
        else:
            messages.error(request, f"Ticket #{ticket.id} is closed already.")
    elif 'set_in_progress' in request.GET:
        ticket_id = request.GET.get('set_in_progress')
        ticket = get_object_or_404(Ticket, id=ticket_id)
        if ticket.is_open():
            ticket.set_in_progress()
            messages.success(request, f"Ticket #{ticket.id} in progress now.")
        else:
            messages.error(request, f"Ticket #{ticket.id} is closed.")
    elif 'reopen_ticket' in request.GET:
        ticket_id = request.GET.get('reopen_ticket')
        ticket = get_object_or_404(Ticket, id=ticket_id)
        if ticket.is_closed():
            ticket.reopen_ticket()
            messages.success(request, f"Ticket #{ticket.id} is opened again.")
        else:
            messages.error(request, f"Ticket #{ticket.id} is opened.")
    elif 'delete_ticket' in request.GET:
        ticket_id = request.GET.get('delete_ticket')
        ticket = get_object_or_404(Ticket, id=ticket_id)
        ticket.delete_ticket()
        messages.success(request, f"Ticket #{ticket.id} is deleted.")

    return render(request, template, context)