from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django import forms
from formtools.wizard.views import SessionWizardView

from .models import Member
from .forms import MyModelForm, MyForm
from .views import MyUpdateView, MyWizardView
from memberdb.account_backend import validate_username, create_ad_user



class AccountForm(MyModelForm):
	# form fields
	username = forms.SlugField(
		validators=[validate_username],
		max_length=19,
	)
	password = forms.CharField(
		min_length=10,
		max_length=127,
		widget=forms.PasswordInput,
		strip=False,
		help_text="Password must be between 10 and 127 characters long"
	)
	confirm_password = forms.CharField(
		min_length=10,
		max_length=127,
		widget=forms.PasswordInput,
		strip=False,
	)

	class Meta:
		model = Member
		fields = ['username']

	def clean(self):
		try:
			if (self['password'].value() != self['confirm_password'].value()):
				self.add_error('confirm_password', 'Passwords must match.')
		except:
			pass
		super().clean();

	def save(self):
		return

class EmailForm(MyModelForm):
	forward = forms.BooleanField(required=False)
	email_address  = forms.EmailField(
		label='Forwarding address (optional)',
		required=False,
		help_text="Your club email will be forwarded to this address. Leave blank if email forwarding is not required"
	)

	class Meta:
		model = Member
		fields = ['forward', 'email_address']

	def clean(self):
		if self['forward'].value() == True:
			try:
				if (len(self['email_address'].value()) == 0):
					self.add_error('email_address', 'Email field cannot be left blankL.')
				if (self['email_address'].value().split('@')[1] in ["ucc.asn.au", "ucc.gu.uwa.edu.au"]):
					self.add_error('email_address', 'Forwarding address cannot be the same as your account address.')
			except:
				pass
		super().clean();

class DispenseForm(MyForm):
	pin = forms.CharField(
		min_length=0,
		max_length=4,
		widget=forms.PasswordInput,
		strip=False,
		required=False,
		help_text="PIN must be 4 digits long")

	confirm_pin = forms.CharField(
		min_length=0,
		max_length=4,
		widget=forms.PasswordInput,
		required=False,
		strip=False,
	)
	def clean(self):
		try:
			if len(self['pin'].value()) != 4 :
				self.add_error('pin', 'PIN must be excatly 4 digits.')
			if not self['pin'].value().isdigit():
				self.add_error('pin', 'PIN can only contain numbers.')
			if (self['pin'].value() != self['confirm_pin'].value()):
				self.add_error('confirm_pin', 'PINs must match.')
		except:
			pass
		super().clean();


class AccountView(MyWizardView):
	form_list = [AccountForm,EmailForm,DispenseForm]
	template_name = 'admin/memberdb/account_create.html'
	admin = None

	def get_form_instance(self, step):
		return self.object

	def get_context_data(self, **kwargs):
		m = self.object
		context = super().get_context_data(**kwargs)
		context.update(self.admin.admin_site.each_context(self.request))
		context.update({
			'opts': self.admin.model._meta,
			'member': m,
		})
		return context


	def done(self, form_list, form_dict, **kwargs):

		# create the user and save their username if successfull
		if create_ad_user(self.get_cleaned_data_for_step('0'), self.object):
			form_list[0].save()


		messages.success(self.request, 'Your membership renewal has been submitted.')
		return HttpResponseRedirect(reverse("admin:memberdb_membership_changelist"))

		#return accountProgressView(self.request, m)


def accountProgressView(request, member):
	return




def accountFinalView():
	return render(request, 'accountfinal.html', context)
