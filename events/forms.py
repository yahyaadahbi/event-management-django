"""
Forms for event creation, editing, and reviews.
"""

from django import forms
from .models import Event, TicketType, Review, EventImage


class EventForm(forms.ModelForm):
    """Multi-step compatible event creation/edit form."""

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'category', 'event_date',
            'location', 'capacity_max', 'price', 'status', 'image', 'is_featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'event_date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
            ),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venue or address'}),
            'capacity_max': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Format datetime for HTML input
        if self.instance and self.instance.pk:
            if self.instance.event_date:
                self.initial['event_date'] = self.instance.event_date.strftime('%Y-%m-%dT%H:%M')


class TicketTypeForm(forms.ModelForm):
    class Meta:
        model = TicketType
        fields = ['name', 'price', 'quantity', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }


TicketTypeFormSet = forms.inlineformset_factory(
    Event, TicketType,
    form=TicketTypeForm,
    extra=1,
    can_delete=True
)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'star-rating-input'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                            'placeholder': 'Share your experience...'}),
        }
