"""
Custom user model with role-based access control.
Extends AbstractUser for flexibility.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    """Extended user model with role, profile info, and avatar."""

    ROLE_CHOICES = [
        ('participant', 'Participant'),
        ('organizer', 'Organizer'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    bookmarks = models.ManyToManyField(
        'events.Event', blank=True, related_name='bookmarked_by'
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_organizer(self):
        return self.role == 'organizer'

    @property
    def is_participant(self):
        return self.role == 'participant'

    def get_avatar_url(self):
        """Return avatar URL or a default placeholder."""
        if self.photo:
            return self.photo.url
        return None


class Notification(models.Model):
    """In-app notifications for users."""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"


class OrganizerRequest(models.Model):
    """Request from participant to become an organizer, reviewed by admin."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organizer_request',
    )
    motivation = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_organizer_requests',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Organizer request: {self.user.username} ({self.status})"
