"""
This file implements the member-facing registration workflow. See ../../README.md
"""

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView
from django import forms

from .models import Member, Membership
from .approve import make_pending_membership

"""
First step: enter an email address and some details (to fill at least a Member model) to create a pending membership.
see https://docs.djangoproject.com/en/2.1/ref/models/fields/#error-messages
and https://docs.djangoproject.com/en/2.1/ref/forms/fields/#error-messages
"""
class RegisterForm(forms.ModelForm):
    confirm_email   = forms.EmailField(label='Confirm your email address', required=False)
    agree_tnc       = forms.BooleanField(label='I agree to the terms & conditions', required=True)
    #membership_type = forms.ChoiceField(label='Select your membership type', required=True, choices=MEMBERSHIP_TYPES)

    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'username', 'phone_number', 'is_student', 'is_guild', 'email_address']
        error_messages = {
            'username': {
                'unique': 'This username is already in use, please pick another one.',
                'invalid': 'Please pick a username with only lowercase letters and numbers'
            }
        }
    
    def clean(self):
        if (self['email_address'].value() != self['confirm_email'].value()):
            self.add_error('email_address', 'Email addresses must match.')
        print(self.errors.as_data())
        super().clean();

    def save(self, commit=True):
        # create a new Member model instance (ie. a record in the Members table) based on submitted form data 
        m = super().save(commit=False)
        if (m.display_name == ""):
            m.display_name = "%s %s" % (m.first_name, m.last_name);
        if (commit):
            m.save()

        # now create a corresponding Membership (marked as pending / not accepted, mostly default values)
        ms = make_pending_membership(m)
        if (commit):
            ms.save();
        return (m, ms)

"""
simple FormView which displays registration form and handles template rendering & form submission
"""
class RegisterView(CreateView):
    template_name = 'register.html'
    form_class = RegisterForm
    model = Member

    """
    called when valid form data has been POSTed
    invalid form data simply redisplays the form with validation errors
    """
    def form_valid(self, form):
        # save the member data and get the Member instance
        m, ms = form.save()
        return HttpResponseRedirect(reverse("memberdb:info", kwargs={'username': m.username}))

class RenewView(UpdateView):
    template_name = 'renew.html'
    form_class = RegisterForm

    def form_valid(self, form):
        pass
