from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Company, Branch, CreditSale, ChequeReceivable
from .serializers import CompanySerializer, BranchSerializer, CreditSaleSerializer, ChequeReceivableSerializer

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