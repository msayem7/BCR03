from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Company, Branch, CreditSale, ChequeReceivable, Customer
from .serializers import CompanySerializer, BranchSerializer, CreditSaleSerializer, ChequeReceivableSerializer, CustomerSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset= Company.objects.all()
    serializer_class= CompanySerializer

class BranchViewSet(viewsets.ModelViewSet):
    queryset= Branch.objects.all()
    serializer_class= BranchSerializer

class CreditSaleViewSet(viewsets.ModelViewSet):
    queryset = CreditSale.objects.all()
    serializer_class = CreditSaleSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CreditSale.objects.all()
    #.filter(user=self.request.user)

    def perform_create(self, serializer):
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


# # views.py
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = 'alias_id'
    lookup_url_kwarg = 'alias_id'
    filterset_fields = ['is_parent', 'parent']

    def create(self, request, *args, **kwargs):
        # alias_id = 'test'
        # request.data.pop('alias_id', alias_id)
        # print(alias_id, request.data)
        return super().create(request, *args, **kwargs)