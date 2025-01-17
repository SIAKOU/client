# payments/urls.py

from django.urls import path
from .views import register_client, make_payment

urlpatterns = [
    path('register/', register_client, name='register_client'),
    path('payment/', make_payment, name='make_payment'),
]