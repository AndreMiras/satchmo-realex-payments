from realex.models import RealexPayments
from django.contrib import admin

class RealexPaymentsAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'realex_order_id', 'realex_pasref',
        'realex_authcode', 'realex_response_code', 'paydate']
    date_hierarchy = 'paydate'
    search_fields = ['realex_order_id', 'realex_pasref', 'realex_authcode']

admin.site.register(RealexPayments, RealexPaymentsAdmin)
