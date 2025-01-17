from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import Workbook
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import ClientForm, PaymentForm
from .models import Payment, Client

import random
import string
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
import requests  # Assurez-vous que requests est importé

def send_receipt(payment):
    subject = 'Reçu de Paiement'
    message = f'Votre paiement de {payment.amount} a été reçu avec succès.\n\nDétails:\nClient: {payment.client.code}\nNuméro de Facture: {payment.invoice_number}\nDate: {payment.payment_date}\nNuméro de Bordereau: {payment.receipt_number}'
    recipient_list = [payment.client.email]  # Assurez-vous que le modèle Client a un champ email
    send_mail(subject, message, 'from@example.com', recipient_list)

def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'payments/register_user.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
    return render(request, 'payments/login.html')

def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def register_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ClientForm()
    return render(request, 'payments/register_client.html', {'form': form})

def make_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            token = generate_token()
            # Appel à l'API de paiement
            response = requests.post('https://api.example.com/payment', json={
                'token': token,
                'client_code': payment.client.code,
                ' amount': payment.amount,
                'invoice_number': payment.invoice_number,
                'receipt_number': payment.receipt_number,
            })
            if response.status_code == 200:
                payment.save()
                send_receipt(payment)
                return redirect('payment_success')
            else:
                return render(request, 'payments/payment_failed.html')
    else:
        form = PaymentForm()
    return render(request, 'payments/make_payment.html', {'form': form})

def export_payments_to_excel(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="paiements.xlsx"'

    wb = Workbook()
    ws = wb.active
    ws.title = "Paiements"

    ws.append(['ID', 'Client', 'Montant', 'Numéro de Facture', 'Date de Paiement', 'Numéro de Bordereau'])

    for payment in Payment.objects.all():
        ws.append([payment.id, payment.client.code, payment.amount, payment.invoice_number, payment.payment_date, payment.receipt_number])

    wb.save(response)
    return response

def export_payments_to_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="paiements.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    p.drawString(100, 750, "Liste des Paiements")

    y = 730
    for payment in Payment.objects.all():
        p.drawString(100, y, f"ID: {payment.id}, Client: {payment.client.code}, Montant: {payment.amount}, Numéro de Facture: {payment.invoice_number}, Date: {payment.payment_date}, Bordereau: {payment.receipt_number}")
        y -= 20

    p.showPage()
    p.save()
    return response