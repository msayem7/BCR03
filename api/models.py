from django.db import models
from cr.chores.chores import generate_unique_id
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Company(models.Model):
    alias_id =  models.CharField(default=generate_unique_id, max_length=10, unique=True, editable=False)
    company_name = models.TextField()
    email = models.EmailField(unique=True)
    mobile = models.TextField(null=False)
    version = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f"{self.name}"
    
class Branch(models.Model):
    alias_id =  models.CharField(default=generate_unique_id, max_length=10, unique=True, editable=False)
    name = models.TextField(blank=False, null=False)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    version = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = "branch"
        verbose_name = "branch"
        verbose_name_plural = "branches"
    
    def __str__(self):
        return f"{self.name}"
    

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
