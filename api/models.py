from django.db import models
from cr.chores.chores import generate_unique_id, generate_alias_id
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
import uuid


class Company(models.Model):
    alias_id =  models.CharField(default=generate_unique_id, max_length=10, unique=True, editable=False)
    company_name = models.TextField()
    email = models.EmailField(unique=True)
    mobile = models.TextField(null=False)
    version = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)


    
    def __str__(self):
        return f"{self.company_name}"  # Use correct field name 

from django.db import models
from django.utils.text import slugify
import uuid

class Branch(models.Model):
    class BranchType(models.IntegerChoices):
        HEAD_OFFICE = 1, 'Head Office'
        BRANCH = 2, 'Branch'

    alias_id = models.SlugField(unique=True, max_length=10, editable=False)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    branch_type = models.IntegerField(choices=BranchType.choices, default=BranchType.BRANCH)
    address = models.TextField(blank=True, null=True)
    contact = models.TextField(blank=True, null=True)
    version = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='branches', null=True, blank=True)
    version = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if not self.alias_id:
            self.alias_id = slugify(str(uuid.uuid4())[:10])
        super().save(*args, **kwargs)

    class Meta:
        db_table = "branch"
        verbose_name = "branch"
        verbose_name_plural = "branches"

    def __str__(self):
        return self.name

# class Branch(models.Model):
#     alias_id =  models.CharField(default=generate_unique_id, max_length=10, unique=True, editable=False)
#     name = models.TextField(blank=False, null=False)
#     company = models.ForeignKey(Company, on_delete=models.PROTECT)
#     version = models.IntegerField(default=0)
#     created_at = models.DateTimeField(default=timezone.now)
    
#     class Meta:
#         db_table = "branch"
#         verbose_name = "branch"
#         verbose_name_plural = "branches"
    
#     def __str__(self):
#         return f"{self.name}"


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
    address = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    