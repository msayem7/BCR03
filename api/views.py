import json
from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction, IntegrityError
from rest_framework.permissions import IsAuthenticated
from .models import (Company, Branch, Customer, CreditInvoice, 
                     ChequeStore, InvoiceChequeMap, MasterClaim)
from .serializers import (CustomTokenObtainPairSerializer, CompanySerializer, 
                          BranchSerializer, CreditInvoiceSerializer, 
                          CustomerSerializer, ChequeStoreSerializer,
                          InvoiceChequeMapSerializer, MasterClaimSerializer)

from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404

from api import serializers


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class BranchViewSet(viewsets.ModelViewSet):
    serializer_class = BranchSerializer
    queryset = Branch.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'alias_id'

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            client_version = int(request.data.get('version'))
            instance = self.get_object()

            # Concurrency check
            if instance.version != client_version:
                return Response(
                    {'version': 'This branch has been modified by another user. Please refresh. current V, client_version v: ' + str(instance.version) + ' ' + str(client_version)},
                    status=status.HTTP_409_CONFLICT
                )

            # Increment version
            new_version = instance.version + 1

            # Partial update handling
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)

            # Save with updated information
            serializer.save(updated_by=request.user, version=new_version)

            return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'alias_id'
    filterset_fields = ['is_parent', 'parent']

    def get_queryset(self):
        queryset = super().get_queryset()
        branch_id = self.request.query_params.get('branch')
        
        print( 'self.request.query_params.get', self.request.query_params.get('is_active', 'true').lower())
           
        #if not self.request.user.is_staff:  # Example: admins see all
        if self.request.query_params.get('is_active'):
            is_active = self.request.query_params.get('is_active', 'true').lower() == 'true'
            print('is_active',is_active, 'self.request.query_params.get', self.request.query_params.get('is_active', 'true').lower())
            queryset = queryset.filter(is_active=is_active)
        
        # Filter by branch alias_id
        if branch_id:
            queryset = queryset.filter(branch__alias_id=branch_id)
            
        # Filter parent customers
        if self.request.query_params.get('is_parent'):
            is_parent = self.request.query_params.get('is_parent', 'true').lower() == 'true'
            queryset = queryset.filter(is_parent=is_parent)
        
        return queryset
    
    def update(self, request, *args, **kwargs):
        if (HasCustomerActivity.has_Activity(self, request)):
            return  Response({'error': 'Customer has active invoices or cheques. Inactivation is not possible'}, status=status.HTTP_409_CONFLICT)
        return super().update(request, *args, **kwargs)


class HasCustomerActivity(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def has_Activity(self, request, *args, **kwargs):
        try:
            customer = get_object_or_404(Customer, alias_id=request.parser_context['kwargs']['alias_id'])
            has_activity = customer.creditinvoice_set.exists() or customer.chequestore_set.exists()
            return has_activity
        except Customer.DoesNotExist:
            return False
        
class CreditInvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = CreditInvoiceSerializer
    queryset = CreditInvoice.objects.all()
    lookup_field = 'alias_id'

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        if branch := params.get('branch'):
            queryset = queryset.filter(branch__alias_id=branch)
        if date_from := params.get('transaction_date_after'):
            queryset = queryset.filter(transaction_date__gte=date_from)
        if date_to := params.get('transaction_date_before'):
            queryset = queryset.filter(transaction_date__lte=date_to)
        if customer := params.get('customer'):
            queryset = queryset.filter(customer__alias_id=customer)
        return queryset

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        # mutable_data = request.data.copy()
        # mutable_data['version'] = int(request.data['version']) + 1

        instance = self.get_object()
        if int(request.data.get('version')) != instance.version:
            return Response({'error': 'Version conflict'}, status=status.HTTP_409_CONFLICT)
        
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(
            instance, 
            data=request.data,  # Use the modified copy
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
    #     if 'customer' in validated_data:
    #         validated_data['payment_grace_days'] = validated_data['customer'].grace_days 
        serializer.save(updated_by=request.user, version=instance.version + 1)
        
        return Response(serializer.data)


    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if latest := self.get_queryset().order_by('-updated_at').first():
            response.headers['Last-Modified'] = latest.updated_at.strftime('%a, %d %b %Y %H:%M:%S GMT')
        return response


class ChequeFilter(filters.FilterSet):
    date_from = filters.DateFilter(field_name='received_date', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='received_date', lookup_expr='lte')
    status = filters.BaseInFilter(field_name='cheque_status', lookup_expr='in')

    class Meta:
        model = ChequeStore
        fields = ['customer', 'date_from', 'date_to', 'status']

        
class ChequeStoreViewSet(viewsets.ModelViewSet):
    serializer_class = ChequeStoreSerializer
    queryset = ChequeStore.objects.all()
    lookup_field = 'alias_id'  
    lookup_url_kwarg = 'alias_id'  # Add this line (optional but explicit)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ChequeFilter

    def get_queryset(self):
        queryset = ChequeStore.objects.filter(isActive=True)
        branch = self.request.query_params.get('branch')
        if branch:
            queryset = queryset.filter(branch__alias_id=branch)
        return queryset.order_by('-received_date')

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if int(request.data.get('version')) != instance.version:
            return Response({'error': 'Version conflict'}, status=status.HTTP_409_CONFLICT)
        return super().update(request, *args, **kwargs)

    def perform_create(self, serializer):
        instance = serializer.save()
        invoice_cheques = json.loads(self.request.data.get('invoice_cheques', '[]'))
        self._handle_invoice_cheques(instance, invoice_cheques)

    def perform_update(self, serializer):
        instance = serializer.save()
        invoice_cheques = json.loads(self.request.data.get('invoice_cheques', '[]'))
        instance.invoice_cheques.all().delete()
        self._handle_invoice_cheques(instance, invoice_cheques)
        
    def _handle_invoice_cheques(self, instance, invoice_cheques):
        for item in invoice_cheques:
            try:
                # Get CreditInvoice instance by alias_id
                credit_invoice = CreditInvoice.objects.get(alias_id=item.get('creditinvoice'))
                
                InvoiceChequeMap.objects.create(
                    cheque_store=instance,
                    creditinvoice=credit_invoice,  # Pass the instance
                    adjusted_amount=item.get('adjusted_amount'),
                    branch=instance.branch,
                    updated_by=instance.updated_by
                )
            except CreditInvoice.DoesNotExist:
                raise serializers.ValidationError(
                    f"Credit invoice with ID {item.get('creditinvoice')} does not exist"
                )
            
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={
            'include_invoice_cheques': request.query_params.get('include_invoice_cheques')
        })
        return Response(serializer.data)
    
class InvoiceChequeMapViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceChequeMapSerializer
    queryset = InvoiceChequeMap.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        branch = self.request.query_params.get('branch')
        if branch:
            queryset = queryset.filter(branch__alias_id=branch)
        return queryset

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if int(request.data.get('version')) != instance.version:
            return Response({'error': 'Version conflict'}, status=status.HTTP_409_CONFLICT)
        return super().update(request, *args, **kwargs)
    



class MasterClaimViewSet(viewsets.ModelViewSet):
    queryset = MasterClaim.objects.all()
    serializer_class = MasterClaimSerializer
    lookup_field = 'alias_id'  

    def get_queryset(self):
        branch = self.request.query_params.get('branch', None)
        if branch:
            return MasterClaim.objects.filter(branch__alias_id=branch)
        return self.queryset #MasterClaim.objects.all()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    # @transaction.atomic
    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     self.perform_destroy(instance)
    #     return Response(status=status.HTTP_204_NO_CONTENT)