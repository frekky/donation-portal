"""
This file implements the door/committee/admin facing membership approval (and payment) interface
See ../../README.md for details
"""
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django import forms

from memberdb.models import Member, Membership, get_membership_type
from memberdb.forms import MyModelForm
from memberdb.views import MyUpdateView

def make_pending_membership(member):
    # check if this member already has a pending membership
    ms = Membership.objects.filter(member=member, approved__exact=False).first()
    if (ms is None):
        ms = Membership(member=member, approved=False)
    ms.date_submitted = timezone.now()
    ms.membership_type = get_membership_type(member)
    return ms

"""
inline admin change list action buttons
see https://medium.com/@hakibenita/how-to-add-custom-action-buttons-to-django-admin-8d266f5b0d41
and have a look at .admin.MembershipAdmin
"""
class MembershipApprovalForm(MyModelForm):
    payment_confirm = forms.BooleanField(label='Confirm payment', required=False)

    class Meta:
        model = Membership
        fields = ['membership_type', 'payment_method']
        widgets = {
            'membership_type': forms.RadioSelect(),
            'payment_method': forms.RadioSelect(),
        }

    """
    Called to validate the data on the form.
    here we fill out some fields automatically (ie. approver, date paid / approved, etc.)
    TODO: deal with account activation/creation, etc.
    """
    def clean(self):
        # get the cleaned data from the form API and do something with it
        data = super().clean()
        now = timezone.now()
        #breakpoint()
        # find a Member matching our current username
        approver = Member.objects.filter(username__exact=self.request.user.username).first()
        if (approver == None):
            self.add_error(None, 'Cannot set approver: no Member record with username %s' % self.request.user.username)
        data['approver'] = approver
        data['approved'] = True
        data['date_approved'] = now

        if (data['payment_confirm'] == True):
            if (data['payment_method'] == ''):
                self.add_error('payment_method', 'Please select a payment method')
            data['date_paid'] = now
        else:
            data['date_paid'] = None
        
        # make sure "no payment" is recorded for Life Members.
        # XXX this might not actually be the case, since some life members may want to also be financial members (ie. for constitutional voting rights)
        #     and so this is probably more annoying than helpful
        if (data['membership_type'] == ''):
            if (data['payment_method'] != ''):
                self.add_error('payment_method', 'Life members shall not pay membership fees!')
            data['payment_method'] = ''

        return data

    """
    do the stuff, approve the things
    """
    def save(self, commit=True):
        ms = super().save(commit=False)

        # copy attributes not specified in fields
        ms.approver = self.cleaned_data['approver']
        ms.approved = self.cleaned_data['approved']
        ms.date_approved = self.cleaned_data['date_approved']
        ms.date_paid = self.cleaned_data['date_paid']

        # do something
        if (commit):
            ms.save()
        return ms

class MembershipApprovalAdminView(MyUpdateView):
    template_name = 'admin/memberdb/membership_approve.html'
    form_class = MembershipApprovalForm
    model = Membership
    pk_url_kwarg = 'object_id'
    # override with the instance of ModelAdmin
    admin = None

    def get_context_data(self, **kwargs):
        ms = self.get_object()
        context = super().get_context_data(**kwargs)
        context.update(self.admin.admin_site.each_context(self.request))
        context.update({
            'opts': self.admin.model._meta,
            'ms': ms,
            'member': ms.member,
            'show_member_summary': True,
        })
        return context

    """
    called when the approval form is submitted and valid data (according to the form's field types and defined validators) is given
    """
    def form_valid(self, form):
        ms = form.save()
        
        self.admin.message_user(self.request, 'Approve success')
        url = reverse(
            'admin:memberdb_membership_change',
            args=[ms.pk],
            current_app=self.admin.admin_site.name,
        )
        return HttpResponseRedirect(url)


