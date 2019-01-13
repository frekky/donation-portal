import uuid
from django.views.generic.detail import DetailView
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib import messages
from django.conf import settings

import squareconnect
from squareconnect.rest import ApiException
from squareconnect.apis.transactions_api import TransactionsApi
from squareconnect.apis.locations_api import LocationsApi

from .models import CardPayment

class PaymentFormView(DetailView):
    """
    Handles the backend stuff for the Square payment form.
    See https://docs.connect.squareup.com/payments/sqpaymentform/setup
    """

    template_name = 'payment_form.html'

    app_id = None       # square app ID (can be accessed by clients)
    loc_id = None       # square location key (can also be accessed by clients)
    access_key = None   # this is secret
    sqapi = None        # keep an instance of the Square API handy

    model = CardPayment
    slug_field = 'token'
    slug_url_kwarg = 'token'
    query_pk_and_slug = True
    context_object_name = 'payment'

    def __init__(self, *args, **kwargs):
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
        })
        return context

    def post(self, request, *args, **kwargs):
        nonce = request.POST.get('nonce', None)
        if (nonce is None or nonce == ""):
            messages.error(request, "No nonce was generated! Please try reloading the page and submit again.")
            return self.get(request)

        api_inst = TransactionsApi(self.sqapi)

        body = {
            'idempotency_key': self.idempotency_key,
            'card_nonce': nonce,
            'amount_money': {
                'amount': amount,
                'currency': 'AUD'
            }
        }

        try:
            api_response = api_inst.charge(self.loc_id, body)
            messages.success(request, "Your payment of %1.2f was successful.", amount)
        except ApiException as e:
            messages.error(request, "Exception while calling TransactionApi::charge: %s" % e)
        
        # redirect to success URL
        if (self.object.completed_url is None):
            return self.get(request)
        return HttpResponseRedirect(self.object.completed_url)


        

