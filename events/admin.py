"""
Customized admin configuration for events app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Event, EventImage, TicketType, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'colored_swatch', 'icon', 'event_count')
    search_fields = ('name',)

    def colored_swatch(self, obj):
        return format_html(
            '<span style="background:{}; padding:2px 12px; border-radius:4px;">&nbsp;</span> {}',
            obj.color, obj.color
        )
    colored_swatch.short_description = 'Color'

    def event_count(self, obj):
        return obj.events.count()
    event_count.short_description = 'Events'


class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1


class TicketTypeInline(admin.TabularInline):
    model = TicketType
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'category', 'status', 'event_date',
                    'capacity_max', 'registrations_count', 'views_count', 'price')
    list_filter = ('status', 'category', 'is_featured', 'views_count')
    search_fields = ('title', 'description', 'organizer__username')
    ordering = ('-created_at',)
    inlines = [EventImageInline, TicketTypeInline]
    actions = ['mark_open', 'mark_closed']

    def registrations_count(self, obj):
        return obj.confirmed_registrations_count
    registrations_count.short_description = 'Registrations'

    def mark_open(self, request, queryset):
        queryset.update(status='open')
    mark_open.short_description = 'Mark selected events as Open'

    def mark_closed(self, request, queryset):
        queryset.update(status='closed')
    mark_closed.short_description = 'Mark selected events as Closed'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__username', 'event__title')
