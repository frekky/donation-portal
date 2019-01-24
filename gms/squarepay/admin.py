from django.utils.html import format_html

from gms import admin
from .models import CardPayment, MembershipPayment

class CardPaymentAdmin(admin.ModelAdmin):
    list_display = ['amount', 'date_created', 'is_paid']
    readonly_fields = ['idempotency_key']


class MembershipPaymentAdmin(CardPaymentAdmin):
    list_display = ['amount', 'date_created', 'is_paid', 'membership']

admin.site.register(CardPayment, CardPaymentAdmin)
admin.site.register(MembershipPayment, MembershipPaymentAdmin)
