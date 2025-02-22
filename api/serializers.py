
from rest_framework import serializers
from .models import (Company, Branch, ChequeStore, InvoiceChequeMap, 
                     Customer, CreditInvoice)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email
        }
        return data
    
class CompanySerializer(serializers.ModelSerializer):
    alias_id = serializers.CharField(read_only=True)

    class Meta:
        model = Company
        fields = ['alias_id','company_name', 'email','mobile']
        # fields = '__all__'


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
            'address', 'contact','updated_at', 'version'
        ]
        read_only_fields = ['alias_id', 'version']

        lookup_field = 'alias_id'

        extra_kwargs = {
            'url': {'lookup_field': 'alias_id'}
        }
   
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
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    

    class Meta:
        model = CreditInvoice
        fields = ('alias_id', 'branch', 'invoice_no', 'customer','customer_name', 'transaction_date'
                  ,'due_amount', 'payment_grace_days', 'status', 'version'
                  )
        read_only_fields = ('alias_id', 'version', 'updated_at', 'updated_by')

    def create(self, validated_data):
        validated_data['payment_grace_days'] = validated_data['customer'].grace_days
        return super().create(validated_data)

    # def update(self, instance, validated_data):
    #     if 'customer' in validated_data:
    #         validated_data['payment_grace_days'] = validated_data['customer'].grace_days 

    #     # validated_data['version'] = str(int(instance['version'])+1)
    #     return super().update(instance, validated_data)
    
   
    # ------------------------------------------------
class InvoiceChequeMapSerializer(serializers.ModelSerializer):
    creditinvoice = serializers.SlugRelatedField(slug_field='alias_id', queryset=CreditInvoice.objects.all())
    cheque_store = serializers.SlugRelatedField(slug_field='alias_id', queryset=ChequeStore.objects.all())
    branch = serializers.SlugRelatedField(slug_field='alias_id', queryset=Branch.objects.all())

    class Meta:
        model = InvoiceChequeMap
        fields = '__all__'
        read_only_fields = ('version', 'updated_at', 'updated_by')


class ChequeStoreSerializer(serializers.ModelSerializer):
    invoice_cheques = InvoiceChequeMapSerializer(many=True, required=False)
    branch = serializers.SlugRelatedField(slug_field='alias_id', queryset=Branch.objects.all())
    customer = serializers.SlugRelatedField(slug_field='alias_id', queryset=Customer.objects.all())
    customer_name = serializers.CharField(source='customer.name', read_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get('include_invoice_cheques'):
            representation['invoice_cheques'] = InvoiceChequeMapSerializer(
                instance.invoice_cheques.all(), many=True
            ).data
        return representation
    
    class Meta:
        model = ChequeStore
        fields = ('alias_id', 'branch', 'customer', 'customer_name','received_date', 'cheque_date'
                  , 'cheque_amount','cheque_detail', 'cheque_status', 'Notes'
                    , 'updated_at', 'updated_by', 'invoice_cheques', 'version')
        read_only_fields = ( 'version', 'updated_at', 'updated_by')

    def validate(self, data):
        if data['received_date'] > timezone.now().date():
            raise serializers.ValidationError("Receiving date cannot be in the future")
        return data

