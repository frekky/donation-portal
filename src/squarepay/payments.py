"""
This file contains functions for dealing with payments (although that's fairly obvious)
"""
import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import squareconnect
from squareconnect.rest import ApiException
from squareconnect.apis.transactions_api import TransactionsApi

log = logging.getLogger('squarepay')

# load the configuration values
app_id = getattr(settings, 'SQUARE_APP_ID', None)
loc_id = getattr(settings, 'SQUARE_LOCATION', None)
access_key = getattr(settings, 'SQUARE_ACCESS_TOKEN', None)

# make sure the configuration values exist
if (app_id is None) or (loc_id is None) or (access_key is None):
    raise ImproperlyConfigured("Please define SQUARE_APP_ID, SQUARE_LOCATION and SQUARE_ACCESS_TOKEN in settings.py")

# instantiate the global squareconnect ApiClient instance (only needs to be done once)
_sqapi_inst = squareconnect.ApiClient()
_sqapi_inst.configuration.access_token = access_key

def get_transactions_api():
    return TransactionsApi(_sqapi_inst)

def try_capture_payment(card_payment, nonce):
    """
    attempt to charge the customer associated with the given card nonce (created by the PaymentForm in JS)
    Note: this can be called multiple times with the same CardPayment instance but the customer will not
    be charged multiple times (using the Square idempotency key feature)
    Returns either True on success or False on failure.
    """
    api_inst = get_transactions_api()

    request_body = {
        'idempotency_key': card_payment.idempotency_key,
        'card_nonce': nonce,
        'amount_money': {
            'amount': card_payment.amount,
            'currency': 'AUD'
        }
    }

    try:
        api_response = api_inst.charge(loc_id, request_body)
        card_payment.set_paid()
        log.info("TransactionApi response without error, charge $%1.2f" % (float(card_payment.amount) / 100.0))
        return True
    except ApiException as e:
        log.error("Exception while calling TransactionApi::charge: %s" % e)
        return False

