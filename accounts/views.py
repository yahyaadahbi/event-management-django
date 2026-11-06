"""
Authentication and profile views.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.utils import timezone
from .forms import RegisterForm, LoginForm, ProfileUpdateForm, OrganizerRoleRequestForm
from .models import Notification, OrganizerRequest
from django.http import JsonResponse


class RegisterView(View):
    """User registration."""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = RegisterForm()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('home')
        return render(request, 'accounts/register.html', {'form': form})


class LoginView(View):
    """Custom login view."""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'home')
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(next_url)
        return render(request, 'accounts/login.html', {'form': form})


class LogoutView(View):
    """Logout and redirect to home."""

    def post(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('home')


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    """View and edit user profile."""

    def get(self, request):
        form = ProfileUpdateForm(instance=request.user)
        organizer_request = OrganizerRequest.objects.filter(user=request.user).first()
        return render(
            request,
            'accounts/profile.html',
            {
                'form': form,
                'organizer_request': organizer_request,
            },
        )

    def post(self, request):
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        organizer_request = OrganizerRequest.objects.filter(user=request.user).first()
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        return render(
            request,
            'accounts/profile.html',
            {
                'form': form,
                'organizer_request': organizer_request,
            },
        )


@method_decorator(login_required, name='dispatch')
class OrganizerRoleRequestView(View):
    """Participant requests organizer role. Admin reviews manually."""

    def get(self, request):
        if request.user.is_organizer or request.user.is_staff:
            messages.info(request, 'Your account already has organizer access.')
            return redirect('profile')

        organizer_request = OrganizerRequest.objects.filter(user=request.user).first()
        form = OrganizerRoleRequestForm(instance=organizer_request)
        return render(
            request,
            'accounts/organizer_request.html',
            {
                'form': form,
                'organizer_request': organizer_request,
            },
        )

    def post(self, request):
        if request.user.is_organizer or request.user.is_staff:
            messages.info(request, 'Your account already has organizer access.')
            return redirect('profile')

        organizer_request = OrganizerRequest.objects.filter(user=request.user).first()

        if organizer_request and organizer_request.status == 'pending':
            messages.warning(request, 'Your organizer request is already pending admin review.')
            return redirect('organizer_request')

        if organizer_request and organizer_request.status == 'approved':
            messages.success(request, 'Your organizer request has already been approved.')
            return redirect('profile')

        form = OrganizerRoleRequestForm(request.POST, instance=organizer_request)
        if form.is_valid():
            organizer_request = form.save(commit=False)
            organizer_request.user = request.user
            organizer_request.status = 'pending'
            organizer_request.reviewed_by = None
            organizer_request.reviewed_at = None
            organizer_request.admin_note = ''
            organizer_request.save()
            messages.success(request, 'Request sent. An admin will review your organizer access request.')
            return redirect('profile')

        return render(
            request,
            'accounts/organizer_request.html',
            {
                'form': form,
                'organizer_request': organizer_request,
            },
        )


@login_required
def mark_notifications_read(request):
    """AJAX: Mark all notifications as read."""
    if request.method == 'POST':
        request.user.notifications.filter(read=False).update(read=True)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)
