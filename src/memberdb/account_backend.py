
import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.translation import gettext_lazy as _

import ldap
import re
import socket

import subprocess
from subprocess import CalledProcessError, TimeoutExpired

import memberdb.models
from datetime import date
from squarepay import dispense


log = logging.getLogger('ldap')
# load config

ldap_uri = getattr(settings, 'AUTH_LDAP_SERVER_URI')
ldap_search_dn = getattr(settings, 'LDAP_USER_SEARCH_DN')
ldap_bind_dn = getattr(settings, 'LDAP_BIND_DN')
ldap_bind_secret = getattr(settings, 'LDAP_BIND_SECRET')
ldap_opts = getattr(settings, 'AUTH_LDAP_GLOBAL_OPTIONS')


#initalise ldap instace
_ldap_inst = ldap.initialize(ldap_uri)
for option,value in ldap_opts.items():
	_ldap_inst.set_option(option,value)

_ldap_inst.set_option(ldap.OPT_X_TLS_NEWCTX, 0)


def get_ldap_instance():
	try:
		_ldap_inst.bind(ldap_bind_dn, ldap_bind_secret)
	except ldap.INVALID_CREDENTIALS:
		log.error("LDAP: Invalid bind credentials")
	except ldap.SERVER_DOWN:
		log.error("LDAP: Cannot Contact LDAP server")

	return _ldap_inst

def get_user_attrs(username, attrs):
	# TODO verify bind
	ld = get_ldap_instance()
	filter = "cn=" + username

	result = ld.search_s(ldap_search_dn, ldap.SCOPE_SUBTREE, filter, attrs)
	if len(result) > 1:
		# multiple accounts matched, this is a problem
		return ldap.NO_UNIQUE_ENTRY
	if len(result) == 0:
		return ldap.NO_SUCH_OBJECT
	return result[0]; 


def get_account_lock_status(username):
	ld = get_ldap_instance()
	try:
		result = get_user_attrs(username, ['userAccountControl'])
	finally:
		ld.unbind()
	return bool(result[1]['userAccountControl'] & 0x002)

def validate_username(value : str):
	# note: slug validator ensures that username only contains [a-z0-9_-]
	# usernames can't begin with a numeric
	if not value[0].isalpha():
		raise ValidationError(
			_('Username must begin with a letter')
		)
	# ensure username is lowercase
	elif not value.islower():
		raise ValidationError(
			_('Username cannot contain uppercase characters')
		)
	# check if the user exists, this test should catch *most* cases
	if subprocess.call(["id", value]) == 0:
		raise ValidationError(_('Username already taken (passwd)'))

	# usernames cannot conflict with hostnames
	try:
		socket.gethostbyname(value)
		raise ValidationError(
			_('Username already taken (CNAME)')
		)
	except socket.gaierror:
		pass	

	# lookup user in ldap, required because not all users are mapped to *nix users
	try:
		if get_user_attrs(value, ['cn']) != ldap.NO_SUCH_OBJECT:
			raise ValidationError(
				_('Username already taken (AD)')
			)
	except ldap.LDAPError:
		log.error("Network error, cannot verify username")
		raise ldap.OPERATIONS_ERROR


		


# locks the specified User Account by performing the following actions:
# 1. set UAC ACCOUNTDISABLE flag (0x002) via ldap
# 2. set user shell to `/etc/locked20xx` via ldap
# 3. do `dispense user type disabled <username> <reason>`
def lock_account(username):
	# TODO: error handling
	ld = get_ldap_instance()
	today = date.today()
	try:
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
def create_account(member, passwd):
	username = "changeme";
	log.info("I: creating new account for %s (%s %s)")


	
	return None;
def create_homes(member):
	return
def set_email_forwarding(member, addr):
	return
def subscribe_to_list(member):
	return
def set_pin(member, pin):
	return



