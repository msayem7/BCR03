from django.contrib import admin

from api.models import ChequeStore, InvoiceChequeMap

# @admin.register(ChequeStore)
# class ChequeStoreAdmin(admin.ModelAdmin):
#     list_display = ('alias_id', 'customer', 'cheque_amount', 'cheque_status')

# @admin.register(InvoiceChequeMap)
# class InvoiceChequeMapAdmin(admin.ModelAdmin):
#     list_display = ('creditinvoice', 'cheque_store', 'adjusted_amount')