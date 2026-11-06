from django.contrib import admin
from .models import Registration
from .utils import generate_qr_code
from django.utils import timezone


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'participant',
        'event',
        'ticket_type',
        'status',
        'payment_status',
        'payment_code',
        'ticket_code',
        'created_at',
    )
    list_filter = ('status', 'payment_status', 'event__category')
    search_fields = ('participant__username', 'event__title', 'ticket_code', 'payment_code')
    ordering = ('-created_at',)
    readonly_fields = (
        'ticket_code',
        'payment_code',
        'payment_submitted_at',
        'validated_by',
        'validated_at',
        'qr_code',
        'created_at',
    )
    actions = ['mark_as_paid', 'mark_payment_rejected', 'cancel_registrations']

    def mark_as_paid(self, request, queryset):
        for registration in queryset:
            registration.payment_status = 'paid'
            registration.status = 'confirmed'
            registration.validated_by = request.user
            registration.validated_at = timezone.now()
            if not registration.qr_code:
                registration = generate_qr_code(registration)
            registration.save()
    mark_as_paid.short_description = 'Approve payment and activate ticket'

    def mark_payment_rejected(self, request, queryset):
        queryset.update(payment_status='rejected', status='pending', validated_at=timezone.now())
    mark_payment_rejected.short_description = 'Reject payment (keep registration pending)'

    def cancel_registrations(self, request, queryset):
        queryset.update(status='cancelled')
    cancel_registrations.short_description = 'Mark selected as Cancelled'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if (
            obj.status == 'confirmed'
            and obj.payment_status in ('paid', 'not_required')
            and not obj.qr_code
        ):
            obj = generate_qr_code(obj)
            obj.save()
