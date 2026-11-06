from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('organizer/request/', views.OrganizerRoleRequestView.as_view(), name='organizer_request'),
    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
]
