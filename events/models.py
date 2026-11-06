"""
Events app models: Category, Event, EventImage, TicketType, Review.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse


class Category(models.Model):
    """Event category with color coding and icon."""

    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#6366f1')  # hex color
    icon = models.CharField(max_length=50, default='bi-tag')   # Bootstrap Icons class

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Event(models.Model):
    """Main event model with capacity tracking and status management."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('full', 'Full'),
        ('closed', 'Closed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField()
    location = models.CharField(max_length=300)
    capacity_max = models.PositiveIntegerField(default=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organized_events'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='events'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'pk': self.pk})

    @property
    def confirmed_registrations_count(self):
        return self.registrations.filter(status='confirmed').count()

    @property
    def spots_remaining(self):
        return max(0, self.capacity_max - self.confirmed_registrations_count)

    @property
    def capacity_percentage(self):
        if self.capacity_max == 0:
            return 100
        return min(100, int((self.confirmed_registrations_count / self.capacity_max) * 100))

    @property
    def is_past(self):
        return self.event_date < timezone.now()

    @property
    def is_free(self):
        return self.price == 0

    def update_status(self):
        """Auto-update status based on capacity and dates."""
        if self.is_past:
            self.status = 'closed'
        elif self.spots_remaining == 0:
            self.status = 'full'
        self.save(update_fields=['status'])

    @property
    def trending_score(self):
        """Simple trending algorithm: recent registrations * views."""
        from django.utils import timezone
        from datetime import timedelta
        recent_regs = self.registrations.filter(
            created_at__gte=timezone.now() - timedelta(days=7),
            status='confirmed'
        ).count()
        return recent_regs * 2 + self.views_count


class EventImage(models.Model):
    """Additional images for events (gallery)."""

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='events/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.event.title}"


class TicketType(models.Model):
    """Ticket tiers per event (VIP, Standard, Early Bird)."""

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_types')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    description = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f"{self.name} – {self.event.title}"

    @property
    def sold_count(self):
        return self.registrations.filter(status='confirmed').count()

    @property
    def available(self):
        return max(0, self.quantity - self.sold_count)


class Review(models.Model):
    """User reviews for events."""

    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews'
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
        
    class Meta:
        unique_together = ('user', 'event')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.event.title} ({self.rating}★)"
