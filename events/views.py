"""
Event views: home, list, detail, CRUD for organizers.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from accounts.models import Notification

from .models import Event, Category, Review
from .forms import EventForm, TicketTypeFormSet, ReviewForm
from .filters import EventFilter


class HomeView(View):
    """Landing page with featured events, stats, and trending."""

    def get(self, request):
        featured_events = Event.objects.filter(
            status='open', is_featured=True
        ).select_related('category', 'organizer')[:6]

        # Trending: sorted by trending_score
        trending_events = sorted(
            Event.objects.filter(status='open').select_related('category', 'organizer')[:20],
            key=lambda e: e.trending_score,
            reverse=True
        )[:4]

        upcoming_events = Event.objects.filter(
            status='open', event_date__gte=timezone.now()
        ).select_related('category', 'organizer').order_by('event_date')[:8]

        categories = Category.objects.annotate(event_count=Count('events')).order_by('-event_count')[:8]

        stats = {
            'total_events': Event.objects.filter(status__in=['open', 'closed']).count(),
            'total_users': _get_user_count(),
            'total_registrations': _get_registration_count(),
            'total_categories': Category.objects.count(),
        }

        context = {
            'featured_events': featured_events,
            'trending_events': trending_events,
            'upcoming_events': upcoming_events,
            'categories': categories,
            'stats': stats,
        }
        return render(request, 'events/home.html', context)


def _get_user_count():
    from django.contrib.auth import get_user_model
    return get_user_model().objects.count()


def _get_registration_count():
    from registrations.models import Registration
    return Registration.objects.filter(status='confirmed').count()


class EventListView(View):
    """Filterable, paginated event list."""

    def get(self, request):
        queryset = Event.objects.filter(
            status__in=['open', 'full']
        ).select_related('category', 'organizer').order_by('-created_at')

        event_filter = EventFilter(request.GET, queryset=queryset)
        filtered_qs = event_filter.qs

        paginator = Paginator(filtered_qs, 9)
        page_obj = paginator.get_page(request.GET.get('page'))

        # AJAX: return JSON for dynamic filtering
        if request.headers.get(
            'X-Requested-With') == 'XMLHttpRequest':
            events_data = [
                {
                    'id': e.id,
                    'title': e.title,
                    'location': e.location,
                    'event_date': e.event_date.strftime('%b %d, %Y'),
                    'price': str(e.price),
                    'capacity_percentage': e.capacity_percentage,
                    'spots_remaining': e.spots_remaining,
                    'status': e.status,
                    'url': e.get_absolute_url(),
                    'image': e.image.url if e.image else None,
                    'category_name': e.category.name if e.category else '',
                    'category_color': e.category.color if e.category else '#6366f1',
                }
                for e in page_obj
            ]
            return JsonResponse({
                'events': events_data,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'total_count': filtered_qs.count(),
            })

        categories = Category.objects.all()
        context = {
            'filter': event_filter,
            'page_obj': page_obj,
            'categories': categories,
            'total_count': filtered_qs.count(),
        }
        return render(request, 'events/event_list.html', context)


class EventDetailView(View):
    """Event detail with registration CTA and reviews."""

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        # Increment view count
        Event.objects.filter(pk=pk).update(views_count=event.views_count + 1)

        user_registration = None
        user_review = None
        review_form = ReviewForm()
        is_bookmarked = False

        if request.user.is_authenticated:
            from registrations.models import Registration
            user_registration = Registration.objects.filter(
                participant=request.user, event=event
            ).first()
            user_review = Review.objects.filter(user=request.user, event=event).first()
            is_bookmarked = request.user.bookmarks.filter(pk=pk).exists()

        reviews = event.reviews.select_related('user').order_by('-created_at')
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        ticket_types = event.ticket_types.all()
        gallery_images = event.gallery_images.all()

        context = {
            'event': event,
            'user_registration': user_registration,
            'user_review': user_review,
            'review_form': review_form,
            'reviews': reviews,
            'avg_rating': avg_rating,
            'ticket_types': ticket_types,
            'gallery_images': gallery_images,
            'is_bookmarked': is_bookmarked,
        }
        return render(request, 'events/event_detail.html', context)

    @method_decorator(login_required)
    def post(self, request, pk):
        """Submit a review."""
        event = get_object_or_404(Event, pk=pk)
        # Only participants who attended can review
        form = ReviewForm(request.POST)
        if form.is_valid():
            review, created = Review.objects.update_or_create(
                user=request.user, event=event,
                defaults={'rating': form.cleaned_data['rating'],
                          'comment': form.cleaned_data['comment']}
            )
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok', 'message': 'Review submitted!'})
            messages.success(request, 'Review submitted!')
        return redirect('event_detail', pk=pk)


# ─── Organizer Views ────────────────────────────────────────────────────────


@method_decorator(login_required, name='dispatch')
class CreateEventView(View):
    """Multi-step event creation for organizers."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_organizer and not request.user.is_staff:
            messages.error(request, 'Only organizers can create events.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = EventForm()
        ticket_formset = TicketTypeFormSet()
        return render(request, 'events/event_form.html', {
            'form': form,
            'ticket_formset': ticket_formset,
            'action': 'Create'
        })

    def post(self, request):
        form = EventForm(request.POST, request.FILES)
        ticket_formset = TicketTypeFormSet(request.POST)
        if form.is_valid() and ticket_formset.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            ticket_formset.instance = event
            ticket_formset.save()
            messages.success(request, f'Event "{event.title}" created successfully!')
            return redirect('event_detail', pk=event.pk)
        return render(request, 'events/event_form.html', {
            'form': form,
            'ticket_formset': ticket_formset,
            'action': 'Create'
        })


@method_decorator(login_required, name='dispatch')
class EditEventView(View):
    """Edit an existing event."""

    def get_event(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if event.organizer != request.user and not request.user.is_staff:
            messages.error(request, 'You do not have permission to edit this event.')
            return None, redirect('my_events')
        return event, None

    def get(self, request, pk):
        event, redirect_response = self.get_event(request, pk)
        if redirect_response:
            return redirect_response
        form = EventForm(instance=event)
        ticket_formset = TicketTypeFormSet(instance=event)
        return render(request, 'events/event_form.html', {
            'form': form,
            'ticket_formset': ticket_formset,
            'event': event,
            'action': 'Edit'
        })

    def post(self, request, pk):
        event, redirect_response = self.get_event(request, pk)
        if redirect_response:
            return redirect_response
        form = EventForm(request.POST, request.FILES, instance=event)
        ticket_formset = TicketTypeFormSet(request.POST, instance=event)
        if form.is_valid() and ticket_formset.is_valid():
            event = form.save()
            ticket_formset.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_detail', pk=event.pk)
        return render(request, 'events/event_form.html', {
            'form': form,
            'ticket_formset': ticket_formset,
            'event': event,
            'action': 'Edit'
        })


@method_decorator(login_required, name='dispatch')
class DeleteEventView(View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk, organizer=request.user)
        title = event.title
        event.delete()
        messages.success(request, f'Event "{title}" deleted.')
        return redirect('my_events')


@method_decorator(login_required, name='dispatch')
class MyEventsView(View):
    """Organizer: list of own events with stats."""

    def get(self, request):
        events = Event.objects.filter(
            organizer=request.user
        ).annotate(
            reg_count=Count('registrations', filter=Q(registrations__status='confirmed'))
        ).order_by('-created_at')

        context = {
            'events': events,
            'total_events': events.count(),
            'open_events': events.filter(status='open').count(),
            'total_registrations': sum(e.reg_count for e in events),
        }
        return render(request, 'events/my_events.html', context)


@login_required
def toggle_bookmark(request, pk):
    """AJAX: Toggle event bookmark/favorite."""
    if request.method == 'POST':
        event = get_object_or_404(Event, pk=pk)
        user = request.user
        if user.bookmarks.filter(pk=pk).exists():
            user.bookmarks.remove(event)
            bookmarked = False
        else:
            user.bookmarks.add(event)
            bookmarked = True
            Notification.objects.create(
                user=user,
                message=f'Saved event: {event.title}',
                link=event.get_absolute_url(),
            )
        return JsonResponse({'bookmarked': bookmarked})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def my_bookmarks(request):
    """Participant: saved/bookmarked events."""
    events = request.user.bookmarks.all().select_related('category', 'organizer')
    return render(request, 'events/bookmarks.html', {'events': events})
