from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from django import forms

from .models import Member, IncAssocMember, Membership

def index(request):
    member_list = Member.objects.all()
    context = {
        'member_list': member_list,
    }
    return render(request, 'index.html', context)

def renew(request, username):
    return HttpResponse("Renew your membership now, " + username);

def info(request, username):
    return HttpResponse("Information for user " + username)