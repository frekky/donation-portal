from django.db import models
from django.db.models import F
from django.core.validators import RegexValidator
from django.core.management.utils import get_random_string
from django.urls import reverse
from django.utils import timezone

from squarepay.dispense import get_item_price
import subprocess

import ldap

"""
dictionary of membership types & descriptions, should be updated if these are changed in dispense.
"""
MEMBERSHIP_TYPES = {
	'oday': {
		'dispense':'pseudo:11',
		'desc':'O\' Day Special - first time members only',
		'is_guild':True,
		'is_student':True,
		'must_be_fresh':True,
	},
	'student_and_guild': {
		'dispense':'pseudo:10',
		'desc':'Student and UWA Guild member',
		'is_guild':True,
		'is_student':True,
		'must_be_fresh':False,
	},
	'student_only': {
		'dispense':'pseudo:9',
		'desc':'Student and not UWA Guild member',
		'is_guild':False,
		'is_student':True,
		'must_be_fresh':False,
	},
	'guild_only': {
		'dispense':'pseudo:8',
		'desc':'Non-Student and UWA Guild member',
		'is_guild':True,
		'is_student':False,
		'must_be_fresh':False,
	},
	'non_student': {
		'dispense':'pseudo:7',
		'desc':'Non-Student and not UWA Guild member',
		'is_guild':False,
		'is_student':False,
		'must_be_fresh':False,
	},
	'lifer': {
		'dispense':'',
		'desc':'Life member',
		'is_guild':False,
		'is_student':False,
		'must_be_fresh':False,
	}
}

def get_membership_choices(is_renew=None, get_prices=True):
	"""
	turn MEMBERSHIP_TYPES into a list of choices used by Django
	also dynamically fetch the prices from dispense (if possible)
	"""
	choices = []
	for key, val in MEMBERSHIP_TYPES.items():
		if (val['must_be_fresh'] and is_renew == True):
			# if you have an account already, you don't qualify for the fresher special
			continue
		if (val['dispense'] == '' and is_renew == False):
			# free memberships can only apply to life members, and they will have an existing membership somewhere
			# so this option is only displayed on the renewal form
			continue
		else:
			if get_prices:
				price = get_item_price(val['dispense'])
			else:
				price = None

			if price is not None:
				desc = "%s ($%1.2f)" % (val['desc'], price / 100.0)
				choices += [(key, desc)]
			else:
				# don't display the price
				choices += [(key, val['desc'])]

	return choices

def get_membership_type(member):
	best = 'non_student'
	is_fresh = member.memberships.all().count() == 0
	for i, t in MEMBERSHIP_TYPES.items():
		if (t['must_be_fresh'] == is_fresh and t['is_student'] == member.is_student and t['is_guild'] == member.is_guild):
			best = i
			break
		elif (t['is_student'] == member.is_student and t['is_guild'] == member.is_guild):
			best = i
			break
	return best

def make_pending_membership(member):
    # check if this member already has a pending membership
    ms = Membership.objects.filter(member=member, approved__exact=False).first()
    if (ms is None):
        ms = Membership(member=member, approved=False)
    ms.date_submitted = timezone.now()
    ms.membership_type = get_membership_type(member)
    return ms

def make_token():
	return get_random_string(128)

PAYMENT_METHODS = [
	('dispense', 'Existing dispense credit'),
	('cash', 'Cash (in person)'),
	('card', 'Tap-n-Go via Square (in person)'),
	('online', 'Online payment via Square'),
	('eft', 'Bank transfer'),
	('', 'No payment')
]

ID_TYPES = [
	('student', 'Student ID'),
	('drivers', 'Drivers licence'),
	('passport', 'Passport'),
	('Other', 'Other ID'),
]

ACCOUNT_STATUS = [
		'enabled',
		'disabled',
		'no account'
		]



class IncAssocMember (models.Model):
	"""
	Member record for data we are legally required to keep under Incorporations Act (and make available to members upon request)
	Note: these data should only be changed administratively or with suitable validation since it must be up to date & accurate.
	"""

	first_name      = models.CharField ('Given Name', max_length=200)
	last_name       = models.CharField ('Other Names', max_length=200)
	email_address   = models.EmailField ('Contact email', blank=False)
	updated         = models.DateTimeField ('IncA. info last updated', auto_now=True)
	created         = models.DateTimeField ('When created', auto_now_add=True)

	def __str__ (self):
		return "%s %s <%s>" % (self.first_name, self.last_name, self.email_address)

	class Meta:
		verbose_name = "Incorporations Act member data"
		verbose_name_plural = verbose_name

class Member (IncAssocMember):
	"""
	Member table: only latest information, one record per member
	Some of this data may be required by the UWA Student Guild. Other stuff is just good to know,
	and we don't _need_ to keep historical data for every current/past member.
	Note: Privacy laws are a thing, unless people allow it then we cannot provide this info to members.
	"""



	# data to be entered by user and validated (mostly) manually
	display_name    = models.CharField ('Display name', max_length=200)
	username        = models.SlugField ('Username', max_length=32, null=True, blank=True, unique=False, validators=[RegexValidator(regex='^[a-z0-9._-]*$')])
	phone_number    = models.CharField ('Phone number', max_length=20, blank=False, validators=[RegexValidator(regex='^\+?[0-9() -]+$')])
	is_student      = models.BooleanField ('Student', default=True, blank=True, help_text="Tick this box if you are a current student at a secondary or tertiary institution in WA")
	is_guild        = models.BooleanField ('UWA Guild member', default=True, blank=True)
	id_number       = models.CharField ('Student number or other ID', max_length=255, blank=False, help_text="")
	id_desc			= models.CharField  ('Form of ID provided', max_length=255, blank=False, help_text="Please describe the type of identification provided", choices=ID_TYPES, default="student")

	# data used internally by the system, not to be touched, seen or heard (except when it is)
	member_updated  = models.DateTimeField ('Internal UCC info last updated', auto_now=True)
	login_token     = models.CharField ('Temporary access key', max_length=128, null=True, editable=False, default=make_token)
	email_confirm   = models.BooleanField ('Email address confirmed', null=False, editable=False, default=False)
	studnt_confirm  = models.BooleanField ('Student status confirmed', null=False, editable=False, default=False)
	guild_confirm   = models.BooleanField ('Guild status confirmed', null=False, editable=False, default=False)

	has_account		= models.BooleanField ('Has AD account', null=False, editable=False, default=False)

	# account info
	def get_uid(self):
		result, uid = subprocess.getstatusoutput(["id", "-u", self.username])
		if (result == 0):
			return uid;
		else:
			return None;

	def __str__ (self):
		if (self.display_name != "%s %s" % (self.first_name, self.last_name)):
			name = "%s (%s %s)" % (self.display_name, self.first_name, self.last_name)
		else:
			name = self.display_name
		return "[%s] %s" % (self.username, name)

	class Meta:
		verbose_name = "Internal UCC member record"

class Membership (models.Model):
	"""
	Membership table: store information related to individual (successful/accepted) signups/renewals
	"""

	member          = models.ForeignKey (Member, on_delete=models.CASCADE, related_name='memberships')
	membership_type = models.CharField ('Membership type', max_length=20, blank=True, null=False, choices=get_membership_choices(get_prices=False))
	payment_method  = models.CharField ('Payment method', max_length=10, blank=True, null=True, choices=PAYMENT_METHODS, default=None)
	approved        = models.BooleanField ('Membership approved', default=False)
	approver        = models.ForeignKey (Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_memberships')
	date_submitted  = models.DateTimeField ('Date signed up')
	date_paid       = models.DateTimeField ('Date of payment', blank=True, null=True)
	date_approved   = models.DateTimeField ('Date approved', blank=True, null=True)

	def __str__ (self):
		return "Member [%s] (%s) renewed membership on %s" % (self.member.username, self.member.display_name, self.date_submitted.strftime("%Y-%m-%d"))

	def get_dispense_item(self):
		return MEMBERSHIP_TYPES[self.membership_type]['dispense']

	class Meta:
		verbose_name = "Membership renewal record"
		ordering = ['approved', '-date_submitted']

class TokenConfirmation(models.Model):
	""" keep track of email confirmation tokens etc. and which field to update """
	member          = models.ForeignKey (Member, on_delete=models.CASCADE, related_name='token_confirmations')
	confirm_token   = models.CharField ('unique confirmation URL token', max_length=128, null=False, default=make_token)
	model_field     = models.CharField ('name of BooleanField to update on parent when confirmed', max_length=40, null=False, blank=False)
	created         = models.DateTimeField ('creation date', auto_now_add=True)

	def mark_confirmed(self):
		""" try to mark as confirmed, if error then silently fail """
		try:
			m = self.member
			setattr(m, self.model_field)
			m.save()
			self.delete()
		except Member.DoesNotExist as e:
			pass

	def get_absolute_url(self):
		return reverse('memberdb:email_confirm', kwargs={'pk': self.id, 'token': self.confirm_token})
