"""
This file implements the door/committee/admin facing membership approval (and payment) interface
See ../../README.md for details
"""
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django import forms

from memberdb.models import Member, Membership, get_membership_choices
from memberdb.forms import MyModelForm
from memberdb.views import MyUpdateView


class MembershipApprovalForm(MyModelForm):
	payment_confirm = forms.BooleanField(
		label = 'Confirm payment',
		required = False
	)

	class Meta:
		model = Membership
		fields = ['membership_type', 'payment_method']
		widgets = {
			'membership_type': forms.RadioSelect(),
			'payment_method': forms.RadioSelect(),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# override the model membership_type field so we display all the options with prices
		self.fields['membership_type'].choices = get_membership_choices()
		self.fields['payment_confirm'].initial = (self.instance.date_paid is not None)

	def clean(self):
		"""
		Called to validate the data on the form.
		here we fill out some fields automatically (ie. approver, date paid / approved, etc.)
		TODO: deal with account activation/creation, etc.
		"""
		data = super().clean()
		now = timezone.now()
		approver = self.request.member
		if (approver == None):
			self.add_error(None, 'Cannot set approver: no Member record associated with current session. (username %s)' % self.request.user.username)

		data['approver'] = approver
		data['approved'] = True
		data['date_approved'] = now

		if (data['payment_confirm'] == True):
			if data['payment_method'] == self.instance.payment_method and data['payment_confirm'] == (self.instance.date_paid is not None):
				# check if the payment was already made, preserve the date_paid
				data['date_paid'] = self.instance.date_paid
			else:
				if (data['payment_method'] == ''):
					self.add_error('payment_method', 'Please select a payment method')
				data['date_paid'] = now
		else:
			data['date_paid'] = None

		return data

	def save(self, commit=True):
		""" save the data into a Membership object """
		ms = super().save(commit=False)

		# copy attributes not specified in editable form fields
		ms.approver = self.cleaned_data['approver']
		ms.approved = self.cleaned_data['approved']
		ms.date_approved = self.cleaned_data['date_approved']
		ms.date_paid = self.cleaned_data['date_paid']

		if (commit):
			ms.save()
		return ms

class MembershipApprovalAdminView(MyUpdateView):
	template_name = 'admin/memberdb/membership_approve.html'
	form_class = MembershipApprovalForm
	model = Membership
	pk_url_kwarg = 'object_id'
	# override with the instance of ModelAdmin
	admin = None

	def get_context_data(self, **kwargs):
		ms = self.get_object()
		context = super().get_context_data(**kwargs)
		context.update(self.admin.admin_site.each_context(self.request))
		context.update({
			'opts': self.admin.model._meta,
			'ms': ms,
			'member': ms.member,
			'show_member_summary': True,
		})
		return context

	"""
	called when the approval form is submitted and valid data (according to the form's field types and defined validators) is given
	"""
	def form_valid(self, form):
		ms = form.save()

		self.admin.message_user(self.request, 'Approve success')
		url = reverse(
			'admin:memberdb_membership_changelist',
			args=[],
			current_app=self.admin.admin_site.name,
		)
		return HttpResponseRedirect(url)


