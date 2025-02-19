from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction, IntegrityError
from rest_framework.permissions import IsAuthenticated
from .models import Company, Branch, Customer, CreditInvoice, CreditSale, ChequeReceivable
from .serializers import (CustomTokenObtainPairSerializer, CompanySerializer, BranchSerializer, CreditSaleSerializer,
                          CreditInvoiceSerializer, ChequeReceivableSerializer, CustomerSerializer)

from rest_framework_simplejwt.views import TokenObtainPairView



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
    lookup_url_kwarg = 'alias_id'
    filterset_fields = ['is_parent', 'parent']

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

# class CreditSaleViewSet(viewsets.ModelViewSet):
#     queryset = CreditSale.objects.all()
#     serializer_class = CreditSaleSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return CreditSale.objects.all()

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

# class ChequeReceivableViewSet(viewsets.ModelViewSet):
#     queryset = ChequeReceivable.objects.all()
#     serializer_class = ChequeReceivableSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return ChequeReceivable.objects.filter(credit_sale__user=self.request.user)

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


