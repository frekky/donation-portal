import uuid
from django.views.generic.base import RedirectView, View
from django.views.generic.detail import DetailView
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from .models import CardPayment
from . import payments
from .payments import try_capture_payment, log

class PaymentFormMixin:
    template_name = 'payment_form.html'
    context_object_name = 'payment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        amount = "$%1.2f AUD" % (self.get_object().amount / 100.0)
        context.update({
            'app_id': payments.app_id,
            'loc_id': payments.loc_id,
            'amount': amount,
        })
        return context

    def payment_success(self, payment):
        payment.set_paid()
        messages.success(self.request, "Your payment of $%1.2f was successful." % (payment.amount / 100.0))

    def payment_error(self, payment):
        messages.error(self.request, "Your payment of $%1.2f was unsuccessful. Please try again later." % (payment.amount / 100.0))
        payment.delete()

    def post(self, request, *args, **kwargs):
        nonce = request.POST.get('nonce', None)
        card_payment = self.get_object()
        amount_aud = card_payment.amount / 100.0

        if (nonce is None or nonce == ""):
            messages.error(request, "Failed to collect card details. Please reload the page and submit again.")
            return self.get(request)

        if try_capture_payment(card_payment, nonce):
            self.payment_success(card_payment)
        else:
            self.payment_error(card_payment)

        # redirect to success URL, or redisplay the form with a success message if none is given
        return HttpResponseRedirect(self.get_completed_url())

class PaymentFormView(PaymentFormMixin, DetailView):
    """
    Handles the backend stuff for the Square payment form.
    See https://docs.connect.squareup.com/payments/sqpaymentform/setup
    Note: currently unused. see MembershipPaymentView
    """
    model = CardPayment
    slug_field = 'token'
    slug_url_kwarg = 'token'
    query_pk_and_slug = True
    #template_name = 'payment_form.html'

    def get_completed_url(self):
        return self.get_object().get_absolute_url()
