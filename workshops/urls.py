from django.urls import path
from . import views

urlpatterns = [
    # Workshop listing
    path('', views.workshop_list, name='workshop_list'),
    
    # Registration
    path('register/<int:workshop_id>/', views.register_workshop, name='register_workshop'),
    path('registration/success/<int:registration_id>/', views.registration_success, name='registration_success'),
    
    # Payment
    path('payment/confirm/<int:registration_id>/', views.payment_confirmation, name='payment_confirmation'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/fail/', views.payment_fail, name='payment_fail'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('payment/success/<int:registration_id>/', views.payment_success_page, name='payment_success_page'),
    
    # Receipt
    path('receipt/download/<int:registration_id>/', views.download_receipt, name='download_receipt'),
    path('receipt/view/<int:registration_id>/', views.view_receipt, name='view_receipt'),
    
    # Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
