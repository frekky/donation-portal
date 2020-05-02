from django.db import models
from django.contrib.auth import get_user_model

from squarepay.models import CardPayment

# Create your models here.
class BalanceAccount(models.Model):
    name            = models.CharField('Account name', max_length=80, blank=False, null=False)
    user            = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, related_name='balances')
    balance_cents   = models.IntegerField('Account balance in cents', null=False, default=0)
    is_charitable   = models.BooleanField('Can be recipient of donations', null=False, default=False)
    date_created    = models.DateTimeField(auto_now_add=True)
    date_updated    = models.DateTimeField(auto_now=True)

# this is basically a Transaction but only for Charity Purposes
class Donation(models.Model):
    amount_cents    = models.IntegerField('Donation amount', null=False, blank=False)
    acct_from       = models.ForeignKey(BalanceAccount, on_delete=models.PROTECT, related_name='donations_from_me')
    acct_to         = models.ForeignKey(BalanceAccount, on_delete=models.PROTECT, related_name='donations_to_me')
    date            = models.DateTimeField(auto_now_add=True)
    payment         = models.ForeignKey(CardPayment, on_delete=models.SET_NULL, null=True, related_name='+')
