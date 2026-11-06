"""
Django-filter configuration for Event model.
Supports search, category, status, price range, and date filtering.
"""

import django_filters
from django import forms
from django.db import models  # moved to top (clean)
from .models import Event, Category


class EventFilter(django_filters.FilterSet):
    """Comprehensive event filter for the event list page."""

    search = django_filters.CharFilter(
        method='filter_search',
        label='Search',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search events...',
            'id': 'search-input'
        })
    )

    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # ✅ FIXED (replaced ChoiceFilter)
    status = django_filters.CharFilter(
        method='filter_status',
        widget=forms.Select(
            choices=[('', 'All Status')] + Event.STATUS_CHOICES,
            attrs={'class': 'form-select'}
        )
    )

    price_min = django_filters.NumberFilter(
        field_name='price', lookup_expr='gte',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min price',
            'min': '0',
            'step': '0.01'
        })
    )

    price_max = django_filters.NumberFilter(
        field_name='price', lookup_expr='lte',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max price',
            'min': '0',
            'step': '0.01'
        })
    )

    date_from = django_filters.DateFilter(
        field_name='event_date', lookup_expr='gte',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    is_free = django_filters.BooleanFilter(
        field_name='price',
        method='filter_free',
        label='Free Only',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Event
        fields = ['search', 'category', 'status', 'price_min', 'price_max', 'date_from']

    def filter_search(self, queryset, name, value):
        """Search by title, description, or location."""
        return queryset.filter(
            models.Q(title__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(location__icontains=value)
        )

    # ✅ NEW (fix for status)
    def filter_status(self, queryset, name, value):
        if value:
            return queryset.filter(status=value)
        return queryset

    def filter_free(self, queryset, name, value):
        if value:
            return queryset.filter(price=0)
        return queryset