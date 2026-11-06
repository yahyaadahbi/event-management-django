"""
Customized admin for accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import CustomUser, Notification, OrganizerRequest


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'phone')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('role', 'photo', 'phone', 'bio')}),
    )

    
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'read', 'created_at')
    list_filter = ('read',)
    search_fields = ('user__username', 'message')


@admin.register(OrganizerRequest)
class OrganizerRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'reviewed_by', 'reviewed_at', 'created_at')
    list_filter = ('status', 'created_at', 'reviewed_at')
    search_fields = ('user__username', 'user__email', 'motivation')
    readonly_fields = ('created_at', 'updated_at')
    actions = ('approve_requests', 'reject_requests')

    @admin.action(description='Approve selected organizer requests')
    def approve_requests(self, request, queryset):
        pending = queryset.exclude(status='approved')
        count = 0
        for organizer_request in pending:
            organizer_request.status = 'approved'
            organizer_request.reviewed_by = request.user
            organizer_request.reviewed_at = timezone.now()
            organizer_request.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_at'])

            user = organizer_request.user
            if user.role != 'organizer':
                user.role = 'organizer'
                user.save(update_fields=['role'])
            count += 1
        self.message_user(request, f'{count} request(s) approved.')

    @admin.action(description='Reject selected organizer requests')
    def reject_requests(self, request, queryset):
        pending = queryset.exclude(status='rejected')
        count = 0
        for organizer_request in pending:
            organizer_request.status = 'rejected'
            organizer_request.reviewed_by = request.user
            organizer_request.reviewed_at = timezone.now()
            organizer_request.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_at'])

            user = organizer_request.user
            if user.role == 'organizer':
                user.role = 'participant'
                user.save(update_fields=['role'])
            count += 1
        self.message_user(request, f'{count} request(s) rejected.')
