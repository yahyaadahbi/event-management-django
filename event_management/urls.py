"""
Root URL configuration for event_management project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from events.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('accounts/', include('accounts.urls')),
    path('events/', include('events.urls')),
    path('registrations/', include('registrations.urls')),
    path('dashboard/', include('dashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom admin site header
admin.site.site_header = "EventHub Administration"
admin.site.site_title = "EventHub Admin"
admin.site.index_title = "Welcome to EventHub Admin"
