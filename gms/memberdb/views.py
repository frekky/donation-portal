from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from django import forms

from .models import Member, IncAssocMember, Membership

class RegisterForm(ModelForm):
    confirm_email = forms.EmailField(label='Confirm your email address')

    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'display_name', 'username', 'phone_number', 'date_of_birth', 'email_address']
        error_messages = {
            'confirm_email': {
                'blank': None,
            }
        }
    
    def clean(self):
        if (self['email_address'].value() != self['confirm_email'].value()):
            self.add_error('email_address', 'Email addresses must match.')
        print(self.errors.as_data())


def index(request):
    member_list = Member.objects.all()
    context = {
        'member_list': member_list,
    }
    return render(request, 'index.html', context)

def renew(request, username):
    return HttpResponse("Renew your membership now, " + username);

def register(request):
    if (request.method == 'POST'):
        form = RegisterForm(request.POST)
        if (form.is_valid()):
            m = form.save();
            return HttpResponseRedirect(reverse("memberdb:info", kwargs={'username': m.username}))
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def info(request, username):
    return HttpResponse("Information for user " + username)