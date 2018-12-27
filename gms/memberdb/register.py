"""
This file implements the member-facing registration workflow. See ../../README.md
"""

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.safestring import mark_safe
from django import forms

from .models import Member, Membership
from .forms import MyModelForm
from .views import MyUpdateView
from .approve import make_pending_membership

"""
First step: enter an email address and some details (to fill at least a Member model) to create a pending membership.
see https://docs.djangoproject.com/en/2.1/ref/models/fields/#error-messages
and https://docs.djangoproject.com/en/2.1/ref/forms/fields/#error-messages
"""
class RegisterForm(MyModelForm):
    confirm_email   = forms.EmailField(label='Confirm your email address', required=False)
    agree_tnc       = forms.BooleanField(label='I agree to the terms & conditions', required=True, help_text=mark_safe(
        "You agree to abide by the UCC Constitution, rulings of the UCC Committee, UCC and "
        "UWA’s Network Usage Guidelines and that you will be subscribed to the UCC Mailing List. <br>"
        'Policies can be found <a href="https://www.ucc.asn.au/infobase/policies.ucc">here</a>.'))
    #membership_type = forms.ChoiceField(label='Select your membership type', required=True, choices=MEMBERSHIP_TYPES)

    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'username', 'phone_number', 'is_student', 'is_guild', 'id_number', 'email_address']
        error_messages = {
            'username': {
                'unique': 'This username is already in use, please pick another one.',
                'invalid': 'Please pick a username with only lowercase letters and numbers'
            }
        }
    
    def clean(self):
        try:
            if (self['email_address'].value() != self['confirm_email'].value()):
                self.add_error('email_address', 'Email addresses must match.')
        except:
            pass
        super().clean();

    def save(self, commit=True):
        # get the Member model instance (ie. a record in the Members table) based on submitted form data 
        m = super().save(commit=False)
        if (m.display_name == ""):
            m.display_name = "%s %s" % (m.first_name, m.last_name);
        if (commit):
            m.save()

        # now create a corresponding Membership (marked as pending / not accepted, mostly default values)
        ms = make_pending_membership(m)
        if (commit):
            ms.save();
        return m, ms

class RenewForm(RegisterForm):
    confirm_email = None
    
    class Meta(RegisterForm.Meta):
        fields = ['first_name', 'last_name', 'phone_number', 'is_student', 'is_guild', 'id_number', 'email_address']

    def save(self, commit=True):
        m, ms = super().save(commit=False)
        m.username = self.request.user.username
        if (commit):
            m.save()
            ms.save()
        return m, ms




"""
simple FormView which displays registration form and handles template rendering & form submission
"""
class RegisterView(MyUpdateView):
    template_name = 'register.html'
    form_class = RegisterForm
    model = Member
    can_create = False

    """
    called when valid form data has been POSTed
    invalid form data simply redisplays the form with validation errors
    """
    def form_valid(self, form):
        # save the member data and get the Member instance
        m, ms = form.save()
        return HttpResponseRedirect(reverse("memberdb:index"))

class RenewView(LoginRequiredMixin, MyUpdateView):
    template_name = 'renew.html'
    form_class = RenewForm
    model = Member

    def get_object(self):
        obj = Member.objects.filter(username__exact=self.request.user.username).first()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'is_new': self.object == None,
        })
        return context

    # get the initial data with which to pre-fill the form
    def get_initial(self):
        data = super().get_initial()
        u = self.request.user
        data.update({
            'first_name': u.first_name,
            'last_name': u.last_name,
            'email_address': u.email,
        })
        return data

    def form_valid(self, form):
        m, ms = form.save()
        return HttpResponseRedirect(reverse("memberdb:index"))
