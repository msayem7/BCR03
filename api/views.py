from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Company, Branch, CreditSale, ChequeReceivable, Customer, Branch
from .serializers import (CompanySerializer, BranchSerializer, CreditSaleSerializer,
                          ChequeReceivableSerializer, CustomerSerializer)
from rest_framework.response import Response
from django.db import transaction

class CompanyViewSet(viewsets.ModelViewSet):
    queryset= Company.objects.all()
    serializer_class= CompanySerializer

class BranchViewSet(viewsets.ModelViewSet):
    serializer_class = BranchSerializer
    queryset = Branch.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'alias_id'

    def update(self, request, *args, **kwargs):

        client_version = request.data.get('version')
        with transaction.atomic():            
            instance = self.get_object()

            # Concurrency check
            if instance.version != client_version:
                return Response(
                    {'version': 'This branch has been modified by another user. Please refresh.'},
                    status=status.HTTP_409_CONFLICT
                )

            # Increment version
            new_version = instance.version + 1

            # Partial update handling
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(
                instance, 
                data=request.data, 
                partial=partial
            )
            serializer.is_valid(raise_exception=True)
            
            # Save with updated information
            serializer.save(
                updated_by=request.user,
                version=new_version
            )

            return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user)


# # views.py
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'alias_id'
    lookup_url_kwarg = 'alias_id'
    filterset_fields = ['is_parent', 'parent']

    def create(self, request, *args, **kwargs):
        # alias_id = 'test'
        # request.data.pop('alias_id', alias_id)
        # print(alias_id, request.data)
        return super().create(request, *args, **kwargs)
    

class CreditSaleViewSet(viewsets.ModelViewSet):
    queryset = CreditSale.objects.all()
    serializer_class = CreditSaleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CreditSale.objects.all()
    #.filter(user=self.request.user)

    def perform_create(self, serializer):
        print(self.request).data
        serializer.save(user=self.request.user)

class ChequeReceivableViewSet(viewsets.ModelViewSet):
    queryset = ChequeReceivable.objects.all()
    serializer_class = ChequeReceivableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChequeReceivable.objects.filter(credit_sale__user=self.request.user)
    
# views.py
# from django_filters import rest_framework as filters

# class OrganizationFilter(filters.FilterSet):
#     class Meta:
#         model = Customer
#         fields = {
#             'is_mother_company': ['exact'],
#             'mother_company': ['exact'],
#         }

# class CustomerViewSet(viewsets.ModelViewSet):
#     queryset = Customer.objects.all()
#     serializer_class = CustomerSerializer
#     filterset_class = OrganizationFilter
#     filter_backends = [filters.DjangoFilterBackend]

