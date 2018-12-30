from datetime import date
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Member, IncAssocMember, Membership
from .forms import MemberHomeForm

def index(request):
    member_list = Member.objects.all()
    context = {
        'member_list': member_list,
    }
    return render(request, 'index.html', context)

def getactive(request):
    actives = Membership.objects.all().select_related('member')
    actives.filter(date_submitted__range=(date(2018, 1, 1), date(2018, 12, 31)))
    context = {
        'member_list': actives,
    }
    return render(request, 'index.html', context)

"""
Can update and create models.
Also passes the request object to the form via its kwargs.
"""
class MyUpdateView(UpdateView):
    can_create = True
    object = None

    def get_object(self):
        if (not self.object is None):
            return self.object
        try:
            sobj = super().get_object()
            if (not sobj is None):
                return sobj
        finally:
            return None

    def get_form_kwargs(self, **kwargs):
        kwargs.update(super().get_form_kwargs())
        kwargs.update({'request': self.request})
        return kwargs

class MemberHomeView(LoginRequiredMixin, MyUpdateView):
    model = Member
    template_name = 'home.html'
    form_class = MemberHomeForm

    def get_object(self):
        return Member.objects.filter(username__exact=self.request.user.username).first()

    def get_context_data(self):
        d = super().get_context_data()
        m = self.get_object()
        d.update({
            'memberships': m.memberships.all() if m is not None else None,
        })
        return d
