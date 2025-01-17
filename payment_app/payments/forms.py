# payments/forms.py

from django import forms
from .models import Client, Payment

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['code', 'location']

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['client', 'amount', 'invoice_number', 'receipt_number']