
import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.translation import gettext_lazy as _

import ldap
import re
import memberdb.models
from datetime import date
from squarepay import dispense


log = logging.getLogger('ldap')
# load config

ldap_uri = getattr(settings, 'AUTH_LDAP_SERVER_URI')
ldap_search_dn = getattr(settings, 'AUTH_LDAP_USER_DN_TEMPLATE')
#ldap_bind_dn = getattr()
#ldap_bind_secret = getattr()


#initalise ldap instace
_ldap_inst = ldap.initialize(ldap_uri)

def get_ldap_instance():
	return _ldap_inst

def get_user_attrs(username, attrs):
	# TODO verify bind
	ld = get_ldap_instance()
	filter = "cn=" + username
	try:
		result = ld.search_s(ldap_search_dn, ldap.SCOPE_SUBTREE, filter, attrs)
		if result.size > 1:
			# multiple accounts matched, this is a problem
			return None
		if result.size == 0:
			# account does not exist
			return None
		return result[0]; 

	except:
		return None

def get_account_lock_status(username):
	ld = get_ldap_instance()
	try:
		ld.bind(ldap_bind_dn, ldap_bind_secret)
		result = get_user_attrs(username, ['userAccountControl'])
	finally:
		ld.unbind()
	return bool(result[1]['userAccountControl'] & 0x002)

def validate_username(value):
	# usernames can't begin with a numeric
	if re.match(r"^\d.*", value):
		log.info("test")
		raise ValidationError(
			_('Username cannot begin with a number'),
			params={'value': value}
		)
	else:
		return value

# locks the specified User Account by performing the following actions:
# 1. set UAC ACCOUNTDISABLE flag (0x002) via ldap
# 2. set user shell to `/etc/locked20xx` via ldap
# 3. do `dispense user type disabled <username> <reason>`
def lock_account(username):
	# TODO: error handling
	ld = get_ldap_instance()
	today = date.today()
	try:
		ld.bind(ldap_bind_dn, ldap_bind_secret)
		# fetch current uac
		result = get_user_attrs(username, ['userAccountControl'])
		
		dn = result[0]
		uac = result[1]['userAccountControl'] | 0x002 # set ACCOUNTDISABLE
		actions = [
			(ldap.MOD_REPLACE, "userAccountControl", uac),
			(ldap.MOD_REPLACE, "userShell", "/etc/locked" + str(today.year))
		]
		# write record
		ld.modify(dn, actions)

	finally:
		ld.unbind()
	
	reason = "account locked by uccportal on %s" % str(today)
	dispense.set_dispense_flag(username, 'disabled', reason)

def unlock_account(username):
	# TODO: error handling
	ld = get_ldap_instance()
	today = date.today()
	try:
		ld.bind(ldap_bind_dn, ldap_bind_secret)
		# fetch current uac
		result = get_user_attrs(username, ['userAccountControl'])
		
		dn = result[0]
		uac = result[1]['userAccountControl'] & ~0x002 # clear ACCOUNTDISABLE
		actions = [
			(ldap.MOD_REPLACE, "userAccountControl",uac),
			(ldap.MOD_REPLACE, "userShell", "/bin/zsh")
		]
		# write record
		ld.modify(dn, actions)

	finally:
		ld.unbind()
	
	reason = "account unlocked by uccportal on %s" % str(today)
	dispense.set_dispense_flag(username, '!disabled', reason)

# Account creation steps:
# 
def create_account(member):
	username = "changeme";
	log.info("I: creating new account for %s (%s %s)")
	
	# prepend student numbers with 'sn'
	if re.fullmatch(r"^2\d{7}$", username):
		log.info("I: username is a student number, adding sn prefix")
		username = sn + username

	# usernames can't begin with a numeric
	if re.match(r"^\d", username):
		log.error("E: The username %s cannot start with a digit." % username)
		return;
	


	
	return None;



