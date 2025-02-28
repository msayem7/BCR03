

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
#media serving to urls.py: 
from django.conf import settings
from django.conf.urls.static import static
from api.views import CustomTokenObtainPairView, user_detail, CIvsChequeReportView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/reports/ci-vs-cheque/', CIvsChequeReportView.as_view({'get': 'list'}), name='ci-cheque-report'),
    path('api/reports/ci-vs-cheque/export_pdf/', CIvsChequeReportView.as_view(actions={'get': 'export_pdf'}), name='ci-cheque-report-pdf'),
    path('api/reports/ci-vs-cheque/export_excel/', CIvsChequeReportView.as_view(actions={'get': 'export_excel'}), name='ci-cheque-report-excel'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/user/', user_detail, name='user_detail'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)