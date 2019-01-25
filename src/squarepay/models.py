import uuid

from django.db import models
from django.urls import reverse

from memberdb.models import Membership, make_token

class CardPayment(models.Model):
    description     = models.CharField('Description', max_length=255)
    amount          = models.IntegerField('Amount in cents', null=False, blank=False)
    idempotency_key = models.CharField('Square Transactions API idempotency key', max_length=64, default=uuid.uuid1)
    is_paid         = models.BooleanField('Has been paid', blank=True, default=False)
    dispense_synced = models.BooleanField('Payment logged in dispense', blank=True, default=False)
    date_created    = models.DateTimeField('Date created', auto_now_add=True)
    date_paid       = models.DateTimeField('Date paid (payment captured)', null=True, blank=True)

class MembershipPayment(CardPayment):
    """
    Link the payment to a specific membership
    """
    membership      = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='payments')
