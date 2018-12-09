from django.http import HttpResponse
from django.shortcuts import render
from .models import Member, IncAssocMember

def index(request):
    member_list = Member.objects.all()
    context = {
        'member_list': member_list,
    }
    return render(request, 'index.html', context)

def renew(request, username):
    return HttpResponse("Renew your membership now, " + username);

def register(request):
    return HttpResponse("Hi there, plz enter your details to register.");

def info(request, username):
    return HttpResponse("Information for user " + username);