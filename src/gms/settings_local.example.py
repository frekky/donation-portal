# Django settings for uccmemberdb project.

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

DEBUG = True

ENV = '${SHORT_ENV_NAME}'

ADMINS = (
	('UCC Committee', 'committee-only@ucc.asn.au'),
)

### Database connection options ###
DATABASES = {
	'default': {
		'ENGINE': '${DB_ENGINE}',     # Add 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
		# this should end up in uccportal/.db/members.db
		'NAME': '${DB_NAME}',   # Or path to database file if using sqlite3.
		'USER': '${DB_USER}',                                 # Not used with sqlite3.
		'PASSWORD': '${DB_SECRET}',                             # Not used with sqlite3.
		'HOST': '${DB_HOST}',                                 # Set to empty string for localhost. Not used with sqlite3.
		'PORT': '',                                 # Set to empty string for default. Not used with sqlite3.
	},
	'memberdb_old': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': 'uccmemberdb_2018',
		'USER': 'uccmemberdb',
		'PASSWORD': '${OLDDB_SECRET}',
		'HOST': 'mussel.ucc.gu.uwa.edu.au',
		'PORT': '',
	}
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = '${APP_SECRET}'

# Set this to whatever your ServerName/ServerAlias(es) are
ALLOWED_HOSTS = ['${DEPLOY_HOST}']

LOG_LEVEL = 'DEBUG'
LOG_FILENAME = os.path.join(ROOT_DIR, "django.log")

import ldap
from django_auth_ldap.config import LDAPSearch, ActiveDirectoryGroupType, LDAPGroupQuery

# LDAP admin settings
LDAP_BASE_DN = 'DC=ad,DC=ucc,DC=gu,DC=uwa,DC=edu,DC=au'
LDAP_USER_SEARCH_DN = 'CN=Users,DC=ad,DC=ucc,DC=gu,DC=uwa,DC=edu,DC=au'
LDAP_BIND_DN = 'CN=uccportal,CN=Users,DC=ad,DC=ucc,DC=gu,DC=uwa,DC=edu,DC=au'
LDAP_BIND_SECRET = "${LDAP_SECRET}"

# this could be ad.ucc.gu.uwa.edu.au but that doesn't resolve externally -
# useful for testing, but should be changed in production so failover works
AUTH_LDAP_SERVER_URI = 'ldaps://ad.ucc.gu.uwa.edu.au/'

# This is also a bad idea, should be changed in production
AUTH_LDAP_GLOBAL_OPTIONS = {
	ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER,
}

# directly attempt to authenticate users to bind to LDAP
AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = True
AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_MIRROR_GROUPS = False
AUTH_LDAP_GROUP_TYPE = ActiveDirectoryGroupType()
AUTH_LDAP_FIND_GROUP_PERMS = False

AUTH_LDAP_USER_DN_TEMPLATE = 'CN=%(user)s,CN=Users,DC=ad,DC=ucc,DC=gu,DC=uwa,DC=edu,DC=au'

AUTH_LDAP_GROUP_SEARCH = LDAPSearch("OU=Groups,DC=ad,DC=ucc,DC=gu,DC=uwa,DC=edu,DC=au",
	ldap.SCOPE_SUBTREE, "(objectClass=group)")

# Populate the Django user from the LDAP directory.
# note: somehow the LDAP/AD users don't have firstName/sn, rather the full name is in name or displayName
AUTH_LDAP_USER_ATTR_MAP = {
	"first_name": "givenName",
	"last_name": "sn",
	"email": "email",
}

ADMIN_ACCESS_QUERY = \
		LDAPGroupQuery("CN=committee,OU=Groups,DC=ad,DC=ucc,DC=gu,DC=uwa,DC=edu,DC=au") | \
		LDAPGroupQuery("CN=door,OU=Groups,DC=ad,DC=ucc,DC=gu,DC=uwa,DC=edu,DC=au") | \
		LDAPGroupQuery("CN=wheel,OU=Groups,DC=ad,DC=ucc,DC=gu,DC=uwa,DC=edu,DC=au")

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
	# staff can login to the admin site
	"is_staff": ADMIN_ACCESS_QUERY,

	# superusers have all permissions (but also need staff to login to admin site)
	"is_superuser": ADMIN_ACCESS_QUERY,
}

# the Square app and location data (set to sandbox unless you want it to charge people)
SQUARE_APP_ID = '${SQUARE_APP_ID}'
SQUARE_LOCATION = '${SQUARE_LOCATION}'
SQUARE_ACCESS_TOKEN = '${SQUARE_SECRET}'

DISPENSE_BIN = '/usr/local/bin/dispense'

# configure the email backend (see https://docs.djangoproject.com/en/2.1/topics/email/)
EMAIL_HOST = "secure.ucc.asn.au"
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = "uccportal"
EMAIL_HOST_PASSWORD = "${EMAIL_SECRET}"
