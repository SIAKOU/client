from django.db import models

# Create your models here.
# payments/models.py

class Client(models.Model):
    code = models.CharField(max_length=80, unique=True)
    location = models.CharField(max_length=120)

    def __str__(self):
        return self.code

class Payment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.FloatField()
    invoice_number = models.CharField(max_length=80)
    payment_date = models.DateTimeField(auto_now_add=True)
    receipt_number = models.CharField(max_length=80)

    def __str__(self):
        return f"Payment {self.id} for {self.client.code}"