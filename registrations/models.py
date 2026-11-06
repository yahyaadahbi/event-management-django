"""
Registration, Ticket, and QR code models.
"""

import uuid
from django.db import models
from django.conf import settings
from events.models import Event, TicketType


class Registration(models.Model):
    """Ticket registration linking a participant to an event."""

    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('not_required', 'Not required'),
        ('pending', 'Pending verification'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
    ]

    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='registrations'
    )
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='registrations'
    )
    ticket_type = models.ForeignKey(
        TicketType, on_delete=models.SET_NULL, null=True, blank=True, related_name='registrations'
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='confirmed')
    payment_status = models.CharField(
        max_length=15, choices=PAYMENT_STATUS_CHOICES, default='not_required'
    )
    payment_code = models.CharField(max_length=16, unique=True, blank=True, null=True)
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    payment_submitted_at = models.DateTimeField(blank=True, null=True)
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='validated_registrations',
    )
    validated_at = models.DateTimeField(blank=True, null=True)
    ticket_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('participant', 'event')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.participant.username} → {self.event.title} [{self.status}]"

    def get_ticket_price(self):
        if self.ticket_type:
            return self.ticket_type.price
        return self.event.price

    def save(self, *args, **kwargs):
        if self.payment_status in ('pending', 'rejected') and not self.payment_code:
            self.payment_code = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)
