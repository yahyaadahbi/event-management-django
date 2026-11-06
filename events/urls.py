from django.urls import path
from . import views

urlpatterns = [
    path('', views.EventListView.as_view(), name='event_list'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('create/', views.CreateEventView.as_view(), name='create_event'),
    path('<int:pk>/edit/', views.EditEventView.as_view(), name='edit_event'),
    path('<int:pk>/delete/', views.DeleteEventView.as_view(), name='delete_event'),
    path('my-events/', views.MyEventsView.as_view(), name='my_events'),
    path('<int:pk>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('bookmarks/', views.my_bookmarks, name='my_bookmarks'),
]
