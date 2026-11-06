from django.urls import path
from . import views

urlpatterns = [
    path('register/<int:event_pk>/', views.RegisterForEventView.as_view(), name='register_event'),
    path('cancel/<int:pk>/', views.CancelRegistrationView.as_view(), name='cancel_registration'),
    path('payment/<int:pk>/submit-proof/', views.SubmitPaymentProofView.as_view(), name='submit_payment_proof'),
    path('my/', views.MyRegistrationsView.as_view(), name='my_registrations'),
    path('ticket/<int:pk>/', views.TicketDetailView.as_view(), name='ticket_detail'),
    path('ticket/<int:pk>/pdf/', views.download_ticket_pdf, name='download_pdf'),
    path('scan/', views.QRScanView.as_view(), name='qr_scan'),
]
