"""
Authentication and profile forms for accounts app.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, OrganizerRequest


class RegisterForm(UserCreationForm):
    """User registration form. New users are always participants."""

    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email address'}
    ))
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ('password1', 'password2'):
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
                'placeholder': 'Password' if field_name == 'password1' else 'Confirm password'
            })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'participant'
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Custom login form with styled inputs."""

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username or Email', 'autofocus': True}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}
    ))


class ProfileUpdateForm(forms.ModelForm):
    """Profile editing form."""

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'bio', 'photo')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


class OrganizerRoleRequestForm(forms.ModelForm):
    """Request organizer role; reviewed manually by admin."""

    class Meta:
        model = OrganizerRequest
        fields = ('motivation',)
        widgets = {
            'motivation': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 6,
                    'placeholder': 'Explain why you need organizer access and what events you plan to host.',
                }
            )
        }
