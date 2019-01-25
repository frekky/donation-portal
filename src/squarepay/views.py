import uuid
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from .models import MembershipPayment, CardPayment
from . import payments
from .payments import try_capture_payment, set_paid

class PaymentFormView(DetailView):
    """
    Handles the backend stuff for the Square payment form.
    See https://docs.connect.squareup.com/payments/sqpaymentform/setup
    """

    template_name = 'payment_form.html'

    model = CardPayment
    slug_field = 'token'
    slug_url_kwarg = 'token'
    query_pk_and_slug = True
    context_object_name = 'payment'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        set_paid(payment)

    def get_completed_url(self):
        return self.get_object().get_absolute_url()

    def post(self, request, *args, **kwargs):
        nonce = request.POST.get('nonce', None)
        card_payment = self.get_object()
        amount_aud = card_payment.amount / 100.0

        if (nonce is None or nonce == ""):
            messages.error(request, "Failed to collect card details. Please reload the page and submit again.")
            return self.get(request)

        if try_capture_payment(card_payment, nonce):
            payment_success(card_payment)
            messages.success(request, "Your payment of $%1.2f was successful." % amount_aud)
        else:
            messages.error(request, "Your payment of $%1.2f was unsuccessful. Please try again later." % amount_aud)
        
        # redirect to success URL, or redisplay the form with a success message if none is given
        return HttpResponseRedirect(self.get_completed_url())

class MembershipPaymentView(PaymentFormView):
    model = MembershipPayment

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if (self.object.membership.date_paid is not None):
            # the membership is already marked as paid, so we add an error and redirect to member home
            messages.error(request, "Your membership is already paid. Check the cokelog (/home/other/coke/cokelog) for more details.")
            return HttpResponseRedirect(self.get_completed_url())
        else:
            return super().dispatch(request, *args, **kwargs)

    def payment_success(self, payment):
        ms = payment.membership
        ms.date_paid = timezone.now()
        ms.payment_method = 'online'
        ms.save()
        super().payment_success(payment)

    def get_completed_url(self):
        return reverse('memberdb:home')
