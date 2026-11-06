"""
Registration views: register, cancel, ticket, PDF download, QR scan.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.http import JsonResponse, HttpResponse

from events.models import Event, TicketType
from .models import Registration
from .utils import generate_qr_code, generate_ticket_pdf, ensure_qr_code
from accounts.models import Notification


@method_decorator(login_required, name='dispatch')
class RegisterForEventView(View):
    """Register the current user for an event (AJAX-friendly)."""

    def post(self, request, event_pk):
        event = get_object_or_404(Event, pk=event_pk)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        # Guard checks
        if event.event_date < timezone.now():
            msg = 'Registration is closed — this event has already ended.'
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': msg}, status=400)
            messages.error(request, msg)
            return redirect('event_detail', pk=event_pk)

        if event.status not in ('open',):
            msg = 'Registrations are not open for this event.'
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': msg})
            messages.error(request, msg)
            return redirect('event_detail', pk=event_pk)

        if event.spots_remaining == 0:
            msg = 'This event is full.'
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': msg})
            messages.error(request, msg)
            return redirect('event_detail', pk=event_pk)

        if Registration.objects.filter(participant=request.user, event=event).exists():
            msg = 'You are already registered for this event.'
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': msg})
            messages.warning(request, msg)
            return redirect('event_detail', pk=event_pk)

        # Ticket type
        ticket_type_id = request.POST.get('ticket_type')
        ticket_type = None
        if ticket_type_id:
            ticket_type = get_object_or_404(TicketType, pk=ticket_type_id, event=event)
            if ticket_type.available == 0:
                msg = 'Selected ticket type is sold out.'
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': msg})
                messages.error(request, msg)
                return redirect('event_detail', pk=event_pk)

        # Create registration
        requires_payment = (ticket_type.price if ticket_type else event.price) > 0
        initial_status = 'pending' if requires_payment else 'confirmed'
        initial_payment_status = 'pending' if requires_payment else 'not_required'
        registration = Registration.objects.create(
            participant=request.user,
            event=event,
            ticket_type=ticket_type,
            status=initial_status,
            payment_status=initial_payment_status,
        )

        # Generate QR code only for validated/free tickets
        if registration.status == 'confirmed':
            registration = generate_qr_code(registration)
            registration.save()

        # Auto-update event status if full
        if event.spots_remaining == 0:
            event.status = 'full'
            event.save(update_fields=['status'])

        # Notification
        Notification.objects.create(
            user=request.user,
            message=(
                f'Payment pending for "{event.title}". Use payment code '
                f'{registration.payment_code}.'
                if requires_payment
                else f'You\'re registered for "{event.title}"! '
                f'Your ticket code is {str(registration.ticket_code)[:8].upper()}...'
            ),
            link=f'/registrations/my/'
        )

        if is_ajax:
            return JsonResponse({
                'status': 'ok',
                'message': (
                    'Registration created. Submit payment proof to activate your ticket.'
                    if requires_payment else 'Registration confirmed!'
                ),
                'ticket_url': f'/registrations/ticket/{registration.pk}/' if not requires_payment else '',
                'spots_remaining': event.spots_remaining,
                'capacity_percentage': event.capacity_percentage,
            })

        if requires_payment:
            messages.info(
                request,
                f'Registration created. Share payment code {registration.payment_code} '
                'and upload payment proof for admin verification.',
            )
            return redirect('my_registrations')
        messages.success(request, f'🎉 You\'re registered for "{event.title}"!')
        return redirect('ticket_detail', pk=registration.pk)


@method_decorator(login_required, name='dispatch')
class CancelRegistrationView(View):
    """Cancel a non-paid registration."""

    def post(self, request, pk):
        registration = get_object_or_404(Registration, pk=pk, participant=request.user)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if registration.payment_status == 'paid':
            msg = 'Paid registrations cannot be cancelled.'
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': msg}, status=400)
            messages.error(request, msg)
            return redirect('my_registrations')

        if registration.status == 'cancelled':
            msg = 'Registration already cancelled.'
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': msg})
            messages.warning(request, msg)
            return redirect('my_registrations')

        registration.status = 'cancelled'
        registration.save()

        # Re-open event if it was full
        event = registration.event
        if event.status == 'full':
            event.status = 'open'
            event.save(update_fields=['status'])

        Notification.objects.create(
            user=request.user,
            message=f'Your registration for "{event.title}" has been cancelled.',
        )

        if is_ajax:
            return JsonResponse({
                'status': 'ok',
                'message': 'Registration cancelled.',
                'spots_remaining': event.spots_remaining,
            })

        messages.info(request, 'Your registration has been cancelled.')
        return redirect('my_registrations')


@method_decorator(login_required, name='dispatch')
class MyRegistrationsView(View):
    """Participant: list of all their registrations."""

    def get(self, request):
        all_registrations = Registration.objects.filter(
            participant=request.user
        ).select_related('event', 'event__category', 'ticket_type').order_by('-created_at')

        registrations = all_registrations.exclude(status='cancelled')

        context = {
            'registrations': registrations,
            'confirmed_count': all_registrations.filter(status='confirmed').count(),
            'cancelled_count': all_registrations.filter(status='cancelled').count(),
            'pending_payment_count': all_registrations.filter(
                status='pending', payment_status='pending'
            ).count(),
        }
        return render(request, 'registrations/my_registrations.html', context)


@method_decorator(login_required, name='dispatch')
class SubmitPaymentProofView(View):
    """Participant uploads payment proof for pending registrations."""

    def post(self, request, pk):
        registration = get_object_or_404(Registration, pk=pk, participant=request.user)

        if registration.status == 'cancelled':
            messages.error(request, 'Cancelled registrations cannot be paid.')
            return redirect('my_registrations')

        if registration.payment_status == 'not_required':
            messages.info(request, 'This registration does not require payment verification.')
            return redirect('my_registrations')

        if not request.FILES.get('payment_proof'):
            messages.error(request, 'Please upload a payment proof image before submitting.')
            return redirect('my_registrations')

        registration.payment_proof = request.FILES['payment_proof']
        registration.payment_status = 'pending'
        registration.status = 'pending'
        registration.payment_submitted_at = timezone.now()
        registration.save(
            update_fields=[
                'payment_proof',
                'payment_status',
                'status',
                'payment_submitted_at',
                'updated_at',
            ]
        )

        Notification.objects.create(
            user=request.user,
            message=f'Payment proof submitted for "{registration.event.title}". Awaiting validation.',
            link='/registrations/my/',
        )
        messages.success(request, 'Payment proof submitted. Admin will review it shortly.')
        return redirect('my_registrations')


@method_decorator(login_required, name='dispatch')
class TicketDetailView(View):
    """View a single ticket with QR code."""

    def get(self, request, pk):
        registration = get_object_or_404(Registration, pk=pk, participant=request.user)
        if registration.status != 'confirmed' or registration.payment_status not in ('paid', 'not_required'):
            messages.warning(request, 'This ticket is not active yet.')
            return redirect('my_registrations')
        registration = ensure_qr_code(registration)
        return render(request, 'registrations/ticket.html', {'registration': registration})


@login_required
def download_ticket_pdf(request, pk):
    """Generate and stream a PDF ticket download."""
    registration = get_object_or_404(Registration, pk=pk, participant=request.user)
    if registration.status != 'confirmed' or registration.payment_status not in ('paid', 'not_required'):
        messages.warning(request, 'This ticket is not active yet.')
        return redirect('my_registrations')
    registration = ensure_qr_code(registration)

    buffer = generate_ticket_pdf(registration)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="ticket-{str(registration.ticket_code)[:8]}.pdf"'
    )
    return response


class QRScanView(View):
    """QR scan validation simulation page (staff/organizer only)."""

    def get(self, request):
        if not request.user.is_authenticated or (
            not request.user.is_organizer and not request.user.is_staff
        ):
            messages.error(request, 'Access denied.')
            return redirect('home')
        return render(request, 'registrations/qr_scan.html')

    def post(self, request):
        """Validate a ticket code."""
        ticket_code = request.POST.get('ticket_code', '').strip()
        try:
            registration = Registration.objects.select_related(
                'participant', 'event', 'ticket_type'
            ).get(ticket_code=ticket_code)
            is_access_valid = registration.status == 'confirmed' and (
                registration.payment_status in ('paid', 'not_required')
            )
            result = {
                'valid': is_access_valid,
                'status': registration.status,
                'payment_status': registration.payment_status,
                'participant': registration.participant.get_full_name() or registration.participant.username,
                'event': registration.event.title,
                'ticket_type': registration.ticket_type.name if registration.ticket_type else 'General',
                'registered_on': registration.created_at.strftime('%Y-%m-%d'),
            }
        except (Registration.DoesNotExist, ValueError):
            result = {'valid': False, 'status': 'not_found', 'error': 'Ticket not found.'}

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(result)
        return render(request, 'registrations/qr_scan.html', {'result': result, 'code': ticket_code})
