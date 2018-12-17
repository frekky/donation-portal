"""
This file implements the member-facing registration workflow. See ../../README.md
"""

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import FormView
from django import forms

from .models import Member, IncAssocMember, Membership

"""
First step: enter an email address and some details (to fill at least a Member model) to create a pending membership.
see https://docs.djangoproject.com/en/2.1/ref/models/fields/#error-messages
and https://docs.djangoproject.com/en/2.1/ref/forms/fields/#error-messages
"""
class RegisterForm(forms.ModelForm):
    confirm_email   = forms.EmailField(label='Confirm your email address', required=False)
    agree_tnc       = forms.BooleanField(label='I agree to the terms & conditions', required=True)

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
        m = super().save(commit=False)
        if (m.display_name == ""):
            m.display_name = "%s %s" % (m.first_name, m.last_name);
        if (commit):
            m.save()
        return m

"""
simple FormView which displays registration form. roughly equivalent to:
def register(request):
    if (request.method == 'POST'):
        form = RegisterForm(request.POST)
        if (form.is_valid()):
            m = form.save();
            return HttpResponseRedirect(reverse("memberdb:info", kwargs={'username': m.username}))
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})
"""
class RegisterView(FormView):
    template_name = 'register.html'
    form_class = RegisterForm

    def form_valid(self, form):
        # called when valid form data has been POSTed
        # invalid form data simply redisplays the form with validation errors
        if (form.is_valid()):
            m = form.save();
            return HttpResponseRedirect(reverse("memberdb:info", kwargs={'username': m.username}))
        else:
            return self.form_invalid(form)
