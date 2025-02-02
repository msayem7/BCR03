from rest_framework import serializers
from .models import CreditSale, ChequeReceivable

class CreditSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditSale
        fields = '__all__'

class ChequeReceivableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChequeReceivable
        fields = '__all__'