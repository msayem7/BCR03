from rest_framework import serializers
from .models import Company, Branch, CreditSale, ChequeReceivable, Customer


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
    version = serializers.IntegerField(read_only=True)
    alias_id = serializers.SlugField(read_only=True)

    class Meta:
        model = Branch
        fields = ['alias_id', 'name', 'parent', 'branch_type', 
                 'address', 'contact', 'version']
        lookup_field = 'alias_id'
        #read_only_fields = ['alias_id', 'created_at', 'updated_at']
        extra_kwargs = {'url': {'lookup_field': 'alias_id'}}

    def create(self, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if instance.version != validated_data.get('version'):
            raise serializers.ValidationError(
                {'version': 'This branch has been modified. Please refresh.'}
            )
        validated_data['updated_by'] = self.context['request'].user
        return super().update(instance, validated_data)

        
# class BranchSerializer(serializers.ModelSerializer):
#     alias_id = serializers.CharField(read_only=True)
#     version = serializers.IntegerField(read_only=True)
#     company_alias_id = serializers.CharField(write_only=True)
#     company = serializers.PrimaryKeyRelatedField(read_only=True)

#     class Meta:
#         model = Branch
#         fields = ['alias_id', 'name', 'company_alias_id', 'company', 'version']

#     def create(self, validated_data):
#         company_alias_id = validated_data.pop('company_alias_id')
#         company = Company.objects.get(alias_id=company_alias_id)
#         branch = Branch.objects.create(company=company, **validated_data)
#         return branch
    
    
class CreditSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditSale
        fields = '__all__'

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
        fields = ['alias_id','branch' 'name', 'is_parent', 'parent'
                  , 'parent_name', 'address', 'phone', 'created_at', 'updated_at']
        read_only_fields = ['alias_id', 'created_at', 'updated_at']
        
        # extra_kwargs = {
        #     'parent': {'required': False}
        # }
