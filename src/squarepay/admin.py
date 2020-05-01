from django.utils.html import format_html

from django.contrib import admin
from .models import CardPayment

class CardPaymentAdmin(admin.ModelAdmin):
    list_display = ['amount', 'date_created', 'is_paid']
    readonly_fields = ['idempotency_key']

admin.site.register(CardPayment, CardPaymentAdmin)
