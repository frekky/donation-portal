from django.utils.html import format_html

from gms import admin
from .models import CardPayment, MembershipPayment

class CardPaymentAdmin(admin.ModelAdmin):
    list_display = ['amount', 'url_field', 'date_created', 'is_paid']
    readonly_fields = ['token', 'idempotency_key']

    def url_field(self, obj):
        return format_html('<a href="{}">Goto payment page</a>', obj.get_absolute_url())
    url_field.short_description = 'Payment URL'
    url_field.allow_tags = True

class MembershipPaymentAdmin(CardPaymentAdmin):
    list_display = ['amount', 'url_field', 'date_created', 'is_paid', 'membership']

admin.site.register(CardPayment, CardPaymentAdmin)
admin.site.register(MembershipPayment, MembershipPaymentAdmin)
