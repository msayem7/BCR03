from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (  ChequeStoreViewSet, CustomerViewSet
                    , BranchViewSet, CreditInvoiceViewSet
                    , InvoiceChequeMapViewSet, MasterClaimViewSet
                    , CustomerClaimViewSet)

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'branches', BranchViewSet)
router.register(r'credit-invoices', CreditInvoiceViewSet)
router.register(r'cheques', ChequeStoreViewSet)
router.register(r'invoice-cheques', InvoiceChequeMapViewSet)
router.register(r'master-claims', MasterClaimViewSet)
router.register(r'customer-claims', CustomerClaimViewSet)

# router.register(r'reports/ci-vs-cheque/', CIvsChequeReportView.as_view(), basename='ci-cheque-report-html')
# router.register(r'reports/ci-vs-cheque/export_excel/', CIvsChequeReportView.as_view(), basename='ci-cheque-report-excel')
# router.register(r'reports/ci-vs-cheque/export_pdf/', CIvsChequeReportView.as_view(), basename='ci-cheque-report-pdf')


#path('reports/ci-vs-cheque/', CIvsChequeReportView.as_view(), name='ci-cheque-report'),
#path('reports/ci-vs-cheque/export_excel/', CIvsChequeReportView.as_view({'get': 'export_excel'}), 
#path('reports/ci-vs-cheque/export_pdf/', CIvsChequeReportView.as_view({'get': 'export_pdf'})),
urlpatterns = [
    path('', include(router.urls)),
]