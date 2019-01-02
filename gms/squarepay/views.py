import uuid
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.conf import settings

import squareconnect
from squareconnect.rest import ApiException
from squareconnect.apis.transactions_api import TransactionsApi
from squareconnect.apis.locations_api import LocationsApi

class PaymentFormView(TemplateView):
    """
    Handles the backend stuff for the Square payment form.
    See https://docs.connect.squareup.com/payments/sqpaymentform/setup
    """

    template_name = 'payment_form.html'
    methods = ['get', 'post']

    app_id = None
    loc_id = None
    access_key = None
    amount = None
    idempotency_key = None
    sqapi = None
    charge_response = None


    def __init__(self, *args, **kwargs):
        self.amount = kwargs.pop('payment_amount', 100)
        super().__init__(*args, **kwargs)

        # get things from settings
        self.app_id = getattr(settings, 'SQUARE_APP_ID', 'bad_config')
        self.loc_id = getattr(settings, 'SQUARE_LOCATION', 'bad_config')
        self.access_key = getattr(settings, 'SQUARE_ACCESS_TOKEN')

        # do some square API client stuff
        self.sqapi = squareconnect.ApiClient()
        self.sqapi.configuration.access_token = self.access_key

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'app_id': self.app_id,
            'loc_id': self.loc_id,
            'response': self.charge_response,
        })
        return context

    def post(self, request, *args, **kwargs):
        nonce = request.POST.get('nonce', None)
        if (nonce is None or nonce == ""):
            messages.error(request, "No nonce was passed or invalid card data.")
            return self.get(request)

        api_inst = TransactionsApi(self.sqapi)

        # this can be reused so we don't double charge the customer
        if (self.idempotency_key is None): 
            self.idempotency_key = str(uuid.uuid1())
        
        body = {
            'idempotency_key': self.idempotency_key,
            'card_nonce': nonce,
            'amount_money': {
                'amount': self.amount,
                'currency': 'AUD'
            }
        }

        try:
            api_response = api_inst.charge(self.loc_id, body)
            self.charge_response = api_response.transaction
        except ApiException as e:
            self.charge_response = None
            messages.error(request, "Exception while calling TransactionApi::charge: %s" % e)
        
        return self.get(request)



        

