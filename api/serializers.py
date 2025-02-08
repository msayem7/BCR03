from rest_framework import serializers
from .models import Company, Branch, CreditSale, ChequeReceivable, Organization


class CompanySerializer(serializers.ModelSerializer):
    alias_id = serializers.CharField(read_only=True)

    class Meta:
        model = Company
        fields = ['alias_id','company_name', 'email','mobile']
        # fields = '__all__'
class BranchSerializer(serializers.ModelSerializer):
    alias_id = serializers.CharField(read_only=True)
    version = serializers.IntegerField(read_only=True)
    company_alias_id = serializers.CharField(write_only=True)
    company = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Branch
        fields = ['alias_id', 'name', 'company_alias_id', 'company', 'version']

    def create(self, validated_data):
        company_alias_id = validated_data.pop('company_alias_id')
        company = Company.objects.get(alias_id=company_alias_id)
        branch = Branch.objects.create(company=company, **validated_data)
        return branch
    
    
class CreditSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditSale
        fields = '__all__'

class ChequeReceivableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChequeReceivable
        fields = '__all__'

#-----------------------------
class OrganizationSerializer(serializers.ModelSerializer):
    mother_company = serializers.SlugRelatedField(
        slug_field='alias_id',
        queryset=Organization.objects.all(),
        required=False,
        allow_null=True
    )
    mother_company_name = serializers.CharField(source='mother_company.name', read_only=True)

    class Meta:
        model = Organization
        fields = ['alias_id', 'name', 'is_mother_company', 'mother_company', 
                 'mother_company_name', 'address', 'phone', 'created_at', 'updated_at']
        read_only_fields = ['alias_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'mother_company': {'required': False}
        }
