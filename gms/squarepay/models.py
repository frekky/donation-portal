import uuid
from django.core.management.utils import get_random_secret_key
from django.db import models
from django.urls import reverse

class CardPayment(models.Model):
    token           = models.CharField('Unique payment token', max_length=64, editable=False, default=get_random_secret_key)
    description     = models.CharField('Description', max_length=255)
    amount          = models.IntegerField('Amount in cents', null=False, blank=False)
    idempotency_key = models.CharField('Square Transactions API idempotency key', max_length=64, editable=False, default=uuid.uuid1)
    is_paid         = models.BooleanField('Has been paid', blank=True, default=False)
    completed_url   = models.CharField('Redirect URL on success', max_length=255, null=True, editable=False)
    dispense_synced = models.BooleanField('Payment lodged in dispense', blank=True, default=False)
    date_created    = models.DateTimeField('Date created', auto_now_add=True)
    date_paid       = models.DateTimeField('Date paid (payment captured)', null=True, blank=True)

    def save(self, *args, **kwargs):
        # generate a token by default. maybe possible using default=...?
        if (self.token is None):
            self.token = get_random_secret_key()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('squarepay:pay', kwargs={ 'pk': self.pk, 'token': self.token })