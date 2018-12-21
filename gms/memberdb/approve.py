"""
This file implements the door/committee/admin facing membership approval (and payment) interface
See ../../README.md for details
"""
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django import forms

from memberdb.models import Member, Membership, MEMBERSHIP_TYPES_

def get_membership_type(member):
    best = None
    is_fresh = member.memberships.all()
    breakpoint()
    for t in MEMBERSHIP_TYPES_:
        pass

"""
inline admin change list action buttons
see https://medium.com/@hakibenita/how-to-add-custom-action-buttons-to-django-admin-8d266f5b0d41
and have a look at .admin.MembershipAdmin
"""
class MembershipApprovalForm(forms.ModelForm):
    payment_amount  = forms.DecimalField(label='Amount paid (AUD)', decimal_places=2, min_value=0)
    payment_confirm = forms.BooleanField(label='Confirm payment', required=True)
    
    # this must be passed by kwargs upon instantiating the form
    request = None

    class Meta:
        model = Membership
        fields = ['membership_type', 'payment_method']
        widgets = {
            'membership_type': forms.RadioSelect(),
            'payment_method': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    """
    Called to validate the data on the form.
    here we fill out some fields automatically (ie. approver, date paid / approved, etc.)
    TODO: deal with account activation/creation, etc.
    """
    def clean(self):
        # get the cleaned data from the form API and do something with it
        data = super().clean()
        breakpoint()
        # find a Member matching our current username
        qs_approver = Member.objects.filter(username__exact=self.request.user.username).first()
        if (qs_approver == None):
            self.add_error(None, 'cannot set approver: no Member record with username %s' % self.request.user.username)

        return data

    """
    do the stuff, approve the things
    """
    def save(self, commit=True):
        ms = super().save(commit=False)
        if (commit):
            ms.save()
        return ms

class MembershipApprovalAdminView(UpdateView):
    template_name = 'admin/memberdb/membership_approve.html'
    form_class = MembershipApprovalForm
    model = Membership
    pk_url_kwarg = 'object_id'
    # override with the instance of ModelAdmin
    admin = None
    object = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.admin.admin_site.each_context(self.request))
        context.update({
            'opts': self.admin.model._meta,
            'member': self.get_object()
        })
        return context

    def get_form_kwargs(self, **kwargs):
        kwargs.update(super().get_form_kwargs())
        kwargs.update({'request': self.request})
        return kwargs

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


