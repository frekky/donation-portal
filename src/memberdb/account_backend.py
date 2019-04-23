
import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.translation import gettext_lazy as _

import re
import socket
from ldap3 import Server, Connection, MODIFY_REPLACE,MODIFY_ADD
from ldap3.core.results import RESULT_SUCCESS
from ldap3.core.exceptions import *


import subprocess
from subprocess import CalledProcessError, TimeoutExpired

import memberdb.models
from datetime import date
from squarepay import dispense

import shutil
import os


log = logging.getLogger('ldap')

# load config
ldap_uri = getattr(settings, 'AUTH_LDAP_SERVER_URI')
ldap_user_dn = getattr(settings, 'LDAP_USER_SEARCH_DN')
ldap_base_dn = getattr(settings, 'LDAP_BASE_DN')
ldap_bind_dn = getattr(settings, 'AUTH_LDAP_BIND_DN')
ldap_bind_secret = getattr(settings, 'AUTH_LDAP_BIND_PASSWORD')
make_home_cmd = ["sudo", "/services/uccportal/src/memberdb/root_actions.py"] 
make_mail_cmd = 'ssh -i %s root@mooneye "/usr/local/mailman/bin/add_members" -r- ucc-announce <<< %s@ucc.asn.au'
make_mail_key = './mooneye.key'


maxuid_dn = "CN=uccdomayne,CN=ypservers,CN=ypServ30,CN=RpcServices,CN=System,"+ldap_base_dn

#initalise ldap instace
_ldap_inst = Connection(
	Server(ldap_uri),
	client_strategy='SYNC',
	user=ldap_bind_dn,
	password=ldap_bind_secret,
	raise_exceptions=True,

	)

# get the ldap instance and bind if required
def get_ldap_instance():
	if not _ldap_inst.bound:
		try:
			_ldap_inst.bind()
		except LDAPInvalidCredentialsResult:
			log.error("LDAP: Invalid bind credentials")
			raise
	return _ldap_inst

def get_ldap_attrs(dn, filter, limit, attrs):
	ld = get_ldap_instance()

	ld.search(dn, filter, size_limit=limit, attributes=attrs)
	result = ld.result
	# fetch matched objects on success
	if (result['result'] == RESULT_SUCCESS):
		entries = ld.entries
	else:
		# otherwise raise an exception
		raise LDAPOperationResult(
			result=result['result'],
			description=result['description'],
			dn=result['dn'],
			message=result['message'],
			response_type=result['type'])

	if len(entries) == 0:
		raise LDAPNoSuchObjectResult()

	return entries;

def get_user_attrs(username, attrs):
	# find the user
	filter = "(cn=" + username + ')'

	result = get_ldap_attrs(ldap_user_dn, filter, 1, attrs)

	return result[0];

def get_maxuid():
	ld = get_ldap_instance()
	filter = "(cn=*)"
	attrs = ['msSFU30MaxUidNumber']
	result = get_ldap_attrs(maxuid_dn, filter, 1, attrs)

	return result[0]

def get_account_lock_status(username):
	ld = get_ldap_instance()
	try:
		result = get_user_attrs(username, ['userAccountControl'])
	# user does not exist
	except LDAPNoSuchObjectResult:
		return None
	# return UAC flag 0x002 ('ACCOUNT_DISABLE')
	return bool(result[1]['userAccountControl'] & 0x002)

def validate_username(value : str):
	# note: slug validator ensures that username only contains [a-z0-9_-]
	# usernames can't begin with a numeric
	if not value[0].isalpha():
		raise ValidationError(_('Username must begin with a letter'))
	# ensure username is lowercase
	if not value.islower():
		raise ValidationError(_('Username cannot contain uppercase characters'))
	# check if the user exists, this test should catch *most* cases
	if subprocess.call(["id", value], stderr=subprocess.DEVNULL) == 0:
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
		get_user_attrs(value, None)
	except LDAPNoSuchObjectResult:
		pass
	else:
		raise ValidationError(_('Username already taken (AD)'))


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

		dn = result.entry_dn
		uac = result['userAccountControl'] | 0x002 # set ACCOUNTDISABLE
		actions = {
			"userAccountControl": [(MODIFY_REPLACE,[uac])],
			"userShell": [(MODIFY_REPLACE,["/etc/locked"+str(today.year)])]
			}
		# write record
		ld.modify(dn, actions)
	except LDAPOperationResult:
		raise
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
		actions = {
			"userAccountControl": [(MODIFY_REPLACE,[uac])],
			"userShell": [(MODIFY_REPLACE,["/bin/zsh"])]
			}
		# write record
		ld.modify(dn, actions)
	except LDAPOperationResult:
		raise
	finally:
		ld.unbind()
	reason = "account unlocked by uccportal on %s" % str(today)
	dispense.set_dispense_flag(username, '!disabled', reason)

# Account creation
def create_ad_user(form_data, member):
	log.info("I: creating new account for %s (%s)")

	# store user details
	# TODO add overides
	username=form_data['username']
	displayName = member.first_name + ' ' + member.last_name
	dn = 'CN=' + username +','+ ldap_user_dn

	# enclose password in quotes and convert to utf16 as required:
	# https://msdn.microsoft.com/en-us/library/cc223248.aspx
	quotedpass = '"'+ form_data['password']+'"'
	utf16pass = quotedpass.encode('utf-16-le')

	# generate uid
	try:
		result = get_maxuid()
	except:
		log.error("LDAP: cannot find base uid")
		raise


	maxuid = int(result.msSFU30MaxUidNumber.value)

	# gets all uids >= maxuid
	# this is done so that we don't encounter the 1000 item limit to ad queries
	entries = get_ldap_attrs(ldap_user_dn,"(uidNumber>=%s)" % maxuid, 100, ['uidNumber'])

	# generate a new uid
	uids = []
	for user in entries:
		uids.append(int(user.uidNumber.value))

	uids.sort()
	# use max uid if it is free
	if uids[0] != maxuid:
		newuid = str(maxuid)
	else:
		prev = uids[0]
		for uid in uids:
			if uid - prev > 1:
				newuid = uid + 1
				break;
			prev = uid
		#increment uid
		newuid = str(prev + 1)

	# sanity check: make sure the uid is free
	if subprocess.call(["id", newuid], stderr=subprocess.DEVNULL) == 0:
		log.error("LDAP: uid already taken")
		raise ValueError

	# create the new user struct
	objclass = ['top','posixAccount','person','organizationalPerson','user']
	attrs = {
		'cn' : username,
		'sAMAccountName' : username,
		'givenName' : member.first_name,
		'sn': member.last_name,
		'displayName': displayName,
		'userAccountControl' : '512',
		'unixHomeDirectory' : "/home/ucc/" + username,
		'loginShell' : '/bin/zsh',
		'gidNumber' : '20021',
		'uidNumber' : newuid,
		'gecos' : displayName,
		'mail' : username + '@ucc.gu.uwa.edu.au',
		'unicodePwd': utf16pass
	}

	# commit the new user to AD
	ld = get_ldap_instance()
	result = ld.add(dn, objclass, attrs)
	if not result:
		log.error("LDAP: user add failed")
		raise LDAPOperationsErrorResult

	# set maxuid
	result = ld.modify(maxuid_dn, {'msSFU30MaxUidNumber': [(MODIFY_REPLACE, newuid)]})
	if not result:
		log.warning("LDAP: user created but msSFU30MaxUidNumber not updated")

	ld.unbind();
	return True;

def make_home(formdata, member):
	user = member.username
	mail = formdata['email_address'] if formdata['forward'] else ""
	result = subprocess.call(make_home_cmd + [user, mail])
	if result == 0:
		return True
	else:
		raise CalledProcessError

def subscribe_to_list(member):
	result = os.system(make_mail_cmd % (make_mail_key, member.username))
	if result == 0:
		return True
	else:
		raise CalledProcessError

def set_pin(member, pin):
	return



