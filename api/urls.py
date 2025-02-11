from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreditSaleViewSet, ChequeReceivableViewSet, CustomerViewSet

router = DefaultRouter()
router.register(r'credit-sales', CreditSaleViewSet)
router.register(r'cheque-receivables', ChequeReceivableViewSet)
router.register(r'customers', CustomerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]