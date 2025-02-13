from django.db import models
from cr.inve_lib.inve_lib import generate_slugify_id, generate_alias_id
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image

class Company(models.Model):
    alias_id = models.CharField(default=generate_slugify_id, max_length=10, unique=True, editable=False)
    company_name = models.TextField()
    email = models.EmailField(unique=True)
    mobile = models.TextField(null=False)
    version = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.company_name}"  # Use correct field name

class BranchType(models.IntegerChoices):
    HEAD_OFFICE = 1, 'Head Office'
    BRANCH = 2, 'Branch'

class Branch(models.Model):
    alias_id = models.SlugField(
        max_length=10,
        unique=True,
        editable=False,
        default=generate_slugify_id
    )
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, 
                              null=True, blank=True, related_name='children')
    branch_type = models.IntegerField(choices=BranchType.choices, 
                                     default=BranchType.BRANCH)
    address = models.TextField(blank=True, null=True)
    contact = models.TextField(blank=True, null=True)
    version = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT,
                                  null=True, blank=True)

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

class Customer(models.Model):
    alias_id = models.TextField(
        max_length=10,
        unique=True,
        editable=False,
        default=generate_alias_id
    )
    name = models.TextField()
    is_parent = models.BooleanField(default=False)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children' 
    )
    grace_days = models.IntegerField(default=0, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class CreditInvoice(models.Model):
    alias_id = models.TextField(default=generate_alias_id, max_length=10, unique=True, editable=False)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, blank=False, null=False)
    invoice_no = models.TextField(blank=False, null=False)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, blank=False, null=False)
    transaction_date = models.DateField(blank=False, null=False)
    delivery_man = models.TextField(blank=True, null=True)
    transaction_details = models.TextField(blank=True, null=True)
    due_amount = models.DecimalField(max_digits=18, decimal_places=4)
    payment_grace_days = models.IntegerField(default=0)
    invoice_image = models.ImageField(upload_to='invoices/', null=True)
    status = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='branches', null=True)
    version = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Credit Invoice'
        verbose_name_plural = 'Credit Invoices'

    def __str__(self):
        return self.invoice_no + self.customer.name + str(self.due_amount)