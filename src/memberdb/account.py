from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django import forms

from .models import Member
from .forms import MyModelForm
from .views import MyUpdateView
from memberdb.account_backend import validate_username

class AccountForm(MyModelForm):

	# form fields
	user= forms.SlugField(
		validators=[validate_username]
		)
	forward_email  = forms.EmailField(
		label='Forwarding address(optional)', 
		required=False,
		help_text="Your club email will be forwarded to this address. Leave blank if email forwarding is not required"
	)

	password = forms.CharField(
		min_length=10, 
		max_length=127, 
		widget=forms.PasswordInput, 
		strip=False,
		help_text="Password must be between 10 and 127 characters long") 

	confirm_password = forms.CharField(
		min_length=10, 
		max_length=127, 
		widget=forms.PasswordInput,
		strip=False,
	)


	class Meta:
		model = Member
		fields = ['first_name']
		error_messages = {
			'username': {
				'unique': 'This username is already taken, please pick another one.',
				'invalid': 'Please pick a username with only lowercase letters and numbers'
			}
		}
	def clean(self):
		try:
			user.clean()
			if (self['password'].value() != self['confirm_password'].value()):
				self.add_error('confirm_password', 'Passwords must match.')
			if (self['forward_email'].value().split('@')[1] in ["ucc.asn.au", "ucc.gu.uwa.edu.au"]):
				self.add_error('forward_email', 'Forwarding address cannot be the same as your account address.')
		except:
			pass
		super().clean();

	def save(self):
		return
		
	

class AccountView(MyUpdateView):
	template_name = 'admin/memberdb/account_create.html'
	form_class = AccountForm
	model = Member
	pk_url_kwarg = 'object_id'
	admin = None

	def get_context_data(self, **kwargs):
		m = self.get_object()
		context = super().get_context_data(**kwargs)
		context.update(self.admin.admin_site.each_context(self.request))
		context.update({
			'opts': self.admin.model._meta,
			'member': m,
		})
		return context

	def form_valid(self, form):
		m, ms = form.save()
		messages.success(self.request, 'Your membership renewal has been submitted.')
		return HttpResponseRedirect(reverse("admin:memberdb_membership_summary"))
