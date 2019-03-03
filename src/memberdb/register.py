"""
This file implements the member-facing registration workflow. See ../../README.md
"""
import subprocess
from subprocess import CalledProcessError, TimeoutExpired
from os import path
from datetime import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.contrib import messages
from django import forms
from django.conf import settings

from squarepay.models import MembershipPayment
from squarepay.dispense import get_item_price

from .models import Member, Membership, get_membership_choices, make_pending_membership, MEMBERSHIP_TYPES
from .forms import MyModelForm
from .views import MyUpdateView

"""
First step: enter an email address and some details (to fill at least a Member model) to create a pending membership.
see https://docs.djangoproject.com/en/2.1/ref/models/fields/#error-messages
and https://docs.djangoproject.com/en/2.1/ref/forms/fields/#error-messages
"""
class RegisterRenewForm(MyModelForm):
	confirm_email   = forms.EmailField(label='Confirm your email address', required=False)
	agree_tnc       = forms.BooleanField(label='I agree to the terms & conditions', required=True, help_text=mark_safe(
		"You agree to abide by the UCC Constitution, rulings of the UCC Committee, UCC and "
		"UWA’s Network Usage Guidelines and that you will be subscribed to the UCC Mailing List. <br>"
		'<b>Policies can be found <a href="https://www.ucc.asn.au/infobase/policies.ucc">here</a>.</b>'))
	membership_type = forms.ChoiceField(label='Select your membership type', required=True, choices=get_membership_choices(is_renew=False))

	class Meta:
		model = Member
		fields = ['first_name', 'last_name', 'phone_number', 'is_student', 'is_guild', 'id_number', 'id_desc', 'email_address']
		error_messages = {
			'username': {
				'invalid': 'Please pick a username with only lowercase letters and numbers'
			}
		}

	def clean(self):
		try:
			if (self['email_address'].value() != self['confirm_email'].value()):
				self.add_error('email_address', 'Email addresses must match.')
			if (self['email_address'].value().lower().split('@')[1] in ["ucc.asn.au", "ucc.gu.uwa.edu.au"]):
				self.add_error('email_address', 'Contact address cannot be an UCC address.')
		except:
			pass
		super().clean();

	def save(self, commit=True):
		# get the Member model instance (ie. a record in the Members table) based on submitted form data
		m = super().save(commit=False)
		if (m.display_name == ""):
			m.display_name = "%s %s" % (m.first_name, m.last_name);
		m.has_account = m.get_uid() != None

		# must save otherwise membership creation will fail
		m.save()

		ms = make_pending_membership(m)
		ms.membership_type = self.cleaned_data['membership_type']

		if (commit):
			ms.save();
		return m, ms

class RegisterForm(RegisterRenewForm):
	username = forms.CharField(
		label='Preferred Username (optional)',
		required=False,
		help_text="This will be the username you use to access club systems. You may leave this blank to choose a username later"
	)

	class Meta():
		model = Member
		fields = ['first_name', 'last_name', 'username', 'phone_number', 'is_student', 'is_guild', 'id_number', 'id_desc', 'email_address']


	def clean(self):
		try:
			if (self['email_address'].value() != self['confirm_email'].value()):
				self.add_error('email_address', 'Email addresses must match.')
			if (self['email_address'].value().split('@')[1] in ["ucc.asn.au", "ucc.gu.uwa.edu.au"]):
					self.add_error('email_address', 'Contact address cannot be an UCC address.')
		except:
			pass
		super().clean();


class RenewForm(RegisterRenewForm):
	confirm_email = None
	membership_type = forms.ChoiceField(label='Select your membership type', required=True, choices=get_membership_choices(is_renew=True))

	class Meta:
		model = Member
		fields = ['first_name', 'last_name', 'phone_number', 'is_student', 'is_guild', 'id_number', 'id_desc', 'email_address']
		exclude = ['username']

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

	def get_context_data(self, **kwargs):
		""" update view context with current renewal year """
		context = super().get_context_data(**kwargs)
		context['year'] = timezone.now().year
		return context

	def form_valid(self, form):
		"""
		called when valid form data has been POSTed
		invalid form data simply redisplays the form with validation errors
		"""
		# save the member data and get the Member instance
		m, ms = form.save()
		messages.success(self.request, 'Your registration has been submitted.')

		# don't set the member session info - user can click on the link
		#self.request.session['member_id'] = m.id
		if self.request.user.is_staff:
			return HttpResponseRedirect(reverse("admin:membership-approve",args=[ms.pk]))
		else:
			return thanks_view(self.request, m, ms)

def thanks_view(request, member, ms):
	""" display a thankyou page after registration is completed """
	context = {
		'member': member,
		'ms': ms,
		'login_url': reverse('memberdb:login_member', kwargs={'id' : member.id, 'member_token': member.login_token}),
	}
	return render(request, 'thanks.html', context)

class RenewView(LoginRequiredMixin, RegisterView):
	template_name = 'renew.html'
	form_class = RenewForm
	model = Member

	def get_object(self):
		""" try to get a pending renewal for this year (to edit & resubmit) otherwise create a new one """
		u = self.request.user
		m = self.request.member

		if m is None:
			# this member is not in the DB yet - make a new Member object and prefill some data
			m = Member(username=u.username)
			m.first_name = u.first_name
			m.last_name = u.last_name
			m.email_address = u.email
			m.login_token = None # renewing members won't need this, make sure it is null for security
		return m

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		last_renewal = self.object.get_last_renewal()

		# renew.html says whether a record exists in the DB or not
		context['is_new'] = self.request.member is None

		# let the template check if user has already renewed this year so it displays a warning
		if last_renewal is not None:
			context['last_renewal'] = last_renewal.date_submitted.year
			context['memberships'] = [last_renewal]

		return context

	def form_valid(self, form):
		m, ms = form.save()
		messages.success(self.request, 'Your membership renewal has been submitted.')

		# always redirect to member home on renewal - you can't renew for someone else, and it
		# is confusing if you get redirected to the admin site
		return HttpResponseRedirect(reverse("memberdb:home"))
