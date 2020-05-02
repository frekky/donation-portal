from django.contrib import admin
from .models import BalanceAccount, Donation

# Register your models here.
admin.site.register(BalanceAccount)
admin.site.register(Donation)
