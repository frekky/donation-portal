from datetime import date, timedelta

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from django.contrib import messages
from django.views.generic.base import View
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import AccessMixin
from django.utils import timezone
from formtools.wizard.views import SessionWizardView

from .models import Member, IncAssocMember, Membership, MEMBERSHIP_TYPES, TokenConfirmation
from .forms import MemberHomeForm

class MemberMiddleware:
    """
    Django middleware to get the member info from a particular session
    if logged in, get member from username, otherwise store some metadata in the session thingy
    see https://docs.djangoproject.com/en/2.1/topics/http/sessions/
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        request.member = None

        if request.user.is_authenticated:
            # get the username only when a user is logged in
            # note that request.user will still exist even when the user isn't logged in
            request.member = Member.objects.filter(username__exact=request.user.username).first()

            if request.member is not None:
                # clean the member's auth token because they now have a working login
                request.member.token = None
                request.member.save()

                if request.user.ldap_user is not None:
                    # copy the LDAP groups so templates can access them
                    request.member.groups = list(request.user.ldap_user.group_names)
                else:
                    request.member.groups = [ "gumby" ]

            # request.session is a dictionary-like object, its content is saved in the database
            # and only a session ID is stored as a browser cookie (by default, but is configurable)
            if 'member_id' in request.session:
                # don't store member ID since we look it up by username
                del request.session['member_id']

        elif 'member_id' in request.session:
            request.member = Member.objects.get(id=request.session['member_id'])

        response = self.get_response(request)
        return response

class MemberAccessMixin(AccessMixin):
    """Verify that the current session has a member object associated with it, or that the user is logged in"""
    def dispatch(self, request, *args, **kwargs):
        if (not request.user.is_authenticated) and (request.member is None):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

"""
Can update and create models.
Also passes the request object to the form via its kwargs.
"""
class MyUpdateView(UpdateView):
    object = None

    def get_object(self):
        if (not self.object is None):
            return self.object
        try:
            sobj = super().get_object()
            if (not sobj is None):
                return sobj
        except:
            pass
        return None

    def get_form_kwargs(self, **kwargs):
        kwargs.update(super().get_form_kwargs())
        kwargs.update({'request': self.request})
        return kwargs

class MyWizardView(SessionWizardView):
    object = None

    def get_object(self):
        if (not self.object is None):
            return self.object
        try:
            sobj = super().get_object()
            if (not sobj is None):
                return sobj
        except:
            pass
        return None

    def get_form_kwargs(self, step, **kwargs):
        kwargs.update(super().get_form_kwargs())
        kwargs.update({'request': self.request})
        return kwargs

class MemberHomeView(MemberAccessMixin, MyUpdateView):
    model = Member
    template_name = 'home.html'
    form_class = MemberHomeForm

    def get_object(self):
        return self.request.member

    def get_context_data(self):
        d = super().get_context_data()
        m = self.get_object()

        if m is not None:
            # get a list of all the membership records associated with this member
            ms_list = m.memberships.all()
            d.update({
                'memberships': ms_list,
            })
        return d

    def form_valid(self, form):
        messages.success(self.request, 'Member details updated.')
        messages.warning(self.request, 'Could not update user display name in AD. Please try again once this feature has been implemented.')

        # redisplay the page
        return self.get(self.request)

class MemberTokenView(View):
    """ allow a user to login using a unique (secure) member token """
    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            # look up the member using exact match for token and username, and registered < 7 days ago
            week_ago = timezone.now() - timedelta(days=7)

            try:
                member = Member.objects.get(
                    login_token=kwargs['member_token'],
                    id=kwargs['id'],
                    created__gte=week_ago
                )
            except Member.DoesNotExist:
                raise Http404()

        request.session['member_id'] = member.id
        return HttpResponseRedirect(reverse('memberdb:home'))

class EmailConfirmView(View):
    """ process email confirmations """

    def get(self, request, **kwargs):
        week_ago = timezone.now() - timedelta(days=7)
        try:
            c = TokenConfirmation.objects.get(
                id = kwargs['pk'],
                confirm_token = kwargs['token'],
                created__gte = week_ago
            )
            c.mark_confirmed()
        except:
            pass
        messages.success(request, "Your email address has been confirmed.")
        return HttpResponseRedirect(reverse('memberdb:home'))

