from rest_framework import serializers
from .models import (Company, Branch, CreditSale, ChequeReceivable, 
                     Customer, CreditInvoice)


class CompanySerializer(serializers.ModelSerializer):
    alias_id = serializers.CharField(read_only=True)

    class Meta:
        model = Company
        fields = ['alias_id','company_name', 'email','mobile']
        # fields = '__all__'

from rest_framework import serializers
from .models import Branch


class BranchSerializer(serializers.ModelSerializer):
    parent = serializers.SlugRelatedField(
        slug_field='alias_id',
        queryset=Branch.objects.all(),
        required=False,
        allow_null=True
    )
    branch_type = serializers.IntegerField()
    
    class Meta:
        model = Branch
        fields = [
            'alias_id', 'name', 'parent', 'branch_type',
            'address', 'contact', 'version'
        ]
        read_only_fields = ['alias_id', 'version']
        lookup_field = 'alias_id'
        extra_kwargs = {
            'url': {'lookup_field': 'alias_id'}
        }
   
class ChequeReceivableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChequeReceivable
        fields = '__all__'

#-----------------------------
class CustomerSerializer(serializers.ModelSerializer):

    parent = serializers.SlugRelatedField(
        slug_field='alias_id',
        queryset=Customer.objects.all(),
        required=False,
        allow_null=True
    )
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = Customer
        fields = ['alias_id', 'name', 'is_parent', 'parent'
                  , 'parent_name','grace_days', 'address', 'phone', 'created_at', 'updated_at']
        read_only_fields = ['alias_id', 'created_at', 'updated_at']
        
        # extra_kwargs = {
        #     'parent': {'required': False}
        # }
        
class CreditInvoiceSerializer(serializers.ModelSerializer):
    branch = serializers.SlugRelatedField(slug_field='alias_id', queryset=Branch.objects.all())
    customer = serializers.SlugRelatedField(slug_field='alias_id', queryset=Customer.objects.all())
    payment_grace_days = serializers.IntegerField(read_only=True)

    class Meta:
        model = CreditInvoice
        fields = '__all__'
        read_only_fields = ('alias_id', 'version', 'updated_at', 'updated_by')

    def create(self, validated_data):
        validated_data['payment_grace_days'] = validated_data['customer'].grace_days
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # for edit case, data will remain unchanged. 
        # if 'customer' in validated_data:
        #     validated_data['payment_grace_days'] = validated_data['customer'].grace_days 
        return super().update(instance, validated_data)
    


    
class CreditSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditSale
        fields = '__all__'
