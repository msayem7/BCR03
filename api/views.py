from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import CreditSale, ChequeReceivable
from .serializers import CreditSaleSerializer, ChequeReceivableSerializer

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