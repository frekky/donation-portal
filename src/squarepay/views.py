import uuid
from django.views.generic.base import RedirectView, View
from django.views.generic.detail import DetailView
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from memberdb.views import MemberAccessMixin
from memberdb.models import Membership

from .models import MembershipPayment, CardPayment
from . import payments
from .payments import try_capture_payment, log
from .dispense import get_item_price

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

class PaymentFormView(DetailView, PaymentFormMixin):
    """
    Handles the backend stuff for the Square payment form.
    See https://docs.connect.squareup.com/payments/sqpaymentform/setup
    Note: currently unused. see MembershipPaymentView
    """
    model = CardPayment
    slug_field = 'token'
    slug_url_kwarg = 'token'
    query_pk_and_slug = True

    def get_completed_url(self):
        return self.get_object().get_absolute_url()

class MembershipPaymentView(MemberAccessMixin, PaymentFormMixin, DetailView):
    """ displays the payment form appropriate for the given membership ID for the currently logged in member """

    def get_object(self):
        """ return the appropriate payment for the current membership, or None if no payment should be made """
        if self.request.member is None:
            raise Http404("no member record associated with current session")

        try:
            # find the membership record we are dealing with
            ms = Membership.objects.get(
                id = self.kwargs['pk'], # get the membership with the given ID
                member = self.request.member,
                date_paid__exact = None, # make sure membership itself is not marked as paid
            )

            # try to find a corresponding MembershipPayment record which has not been paid
            payment = MembershipPayment.objects.get(
                date_paid = None, # CardPayment.date_paid
                is_paid = False, # CardPayment.is_paid
                membership = ms, # MembershipPayment.membership
                membership__date_paid__exact = None, # MembershipPayment.membership.date_paid
            )
        except Membership.DoesNotExist as e:
            # no unpaid membership found, return
            log.warning("could not find unpaid membership with id %s" % self.kwargs['pk'])
            return None
        except MembershipPayment.DoesNotExist as e:
            # found an unpaid membership, but no payment record exists yet
            log.info("creating membership payment for membership id %s" % self.kwargs['pk'])
            return create_membership_payment(ms)
        return payment

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.object = self.get_object()

        # don't produce the payment form if get_object() decides we don't have anything to do
        if (self.object is None):
            # the membership is already marked as paid and no CardPayment exists
            # so we add an error and redirect to member home
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

def create_membership_payment(membership, commit=True):
    """ creates a MembershipPayment object for the given membership """
    # get the amount from dispense
    price = get_item_price(membership.get_dispense_item())
    if (price is None or price == 0):
        return None
    desc = membership.get_pretty_type()
    payment = MembershipPayment(description=desc, amount=price, membership=membership)

    if (commit):
        payment.save()
    return payment
