from django.db import models
from django.contrib.auth.models import User

class CreditSale(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sale_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return f"Credit Sale {self.id} by {self.user.username}"

class ChequeReceivable(models.Model):
    credit_sale = models.ForeignKey(CreditSale, on_delete=models.CASCADE)
    cheque_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f"Cheque {self.cheque_number} for {self.amount}"