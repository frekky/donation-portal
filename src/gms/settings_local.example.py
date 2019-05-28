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
		'ENGINE': '${DB_ENGINE}',     # django.db.backends.XXX where XXX is 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
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
LOG_LEVEL_DJANGO = 'WARNING'
LOG_FILENAME = os.path.join(ROOT_DIR, "django.log")

import ldap
from django_auth_ldap.config import LDAPSearch, ActiveDirectoryGroupType, LDAPGroupQuery

# this could be ad.ucc.gu.uwa.edu.au but that doesn't resolve externally -
# useful for testing, but should be changed in production so failover works
AUTH_LDAP_SERVER_URI = 'ldaps://ad.ucc.gu.uwa.edu.au'

# This is also a bad idea, should be changed in production
AUTH_LDAP_GLOBAL_OPTIONS = {
	ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER,
}

# LDAP admin settings - NOT for django_auth_ldap
LDAP_BASE_DN = "DC=ad,DC=ucc,DC=gu,DC=uwa,DC=edu,DC=au"
LDAP_USER_SEARCH_DN = 'CN=Users,' + LDAP_BASE_DN

# settings used by memberdb LDAP backend and django_auth_ldap
AUTH_LDAP_BIND_DN = "CN=uccportal,CN=Users," + LDAP_BASE_DN
AUTH_LDAP_BIND_PASSWORD = "${LDAP_SECRET}"

# just for django_auth_ldap
AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = False
AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_MIRROR_GROUPS = False
AUTH_LDAP_GROUP_TYPE = ActiveDirectoryGroupType()

# give user permissions from Django groups corresponding to names of AD groups
AUTH_LDAP_FIND_GROUP_PERMS = True

# speed it up by not having to search for the username, we can predict the DN
AUTH_LDAP_USER_DN_TEMPLATE = 'CN=%(user)s,CN=Users,' + LDAP_BASE_DN

# this is necessary where the user DN can't be predicted, ie. if the
# user object is named by full name rather than username
#AUTH_LDAP_USER_SEARCH = LDAPSearch('CN=Users,' + LDAP_BASE_DN,
#	ldap.SCOPE_SUBTREE, "(&(objectClass=user)(sAMAccountName=%(user)s))")

AUTH_LDAP_GROUP_SEARCH = LDAPSearch("OU=Groups," + LDAP_BASE_DN,
	ldap.SCOPE_SUBTREE, "(objectClass=group)")

# Populate the Django user from the LDAP directory.
# note: somehow the LDAP/AD users don't have firstName/sn, rather the full name is in name or displayName
AUTH_LDAP_USER_ATTR_MAP = {
	"first_name": "givenName",
	"last_name": "sn",
	"email": "email",
}

DOOR_GROUP_QUERY = LDAPGroupQuery("CN=door,OU=Groups," + LDAP_BASE_DN)
COMMITTEE_GROUP_QUERY = LDAPGroupQuery("CN=committee,OU=Groups," + LDAP_BASE_DN)
WHEEL_GROUP_QUERY = LDAPGroupQuery("CN=wheel,OU=Groups," + LDAP_BASE_DN)

ADMIN_ACCESS_QUERY = COMMITTEE_GROUP_QUERY | DOOR_GROUP_QUERY | WHEEL_GROUP_QUERY

# assign user object flags based on group memberships (independent from permissions)
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
	# staff can login to the admin site
	"is_staff": ADMIN_ACCESS_QUERY,

	# superusers have all permissions (but also need staff to login to admin site)
	"is_superuser": COMMITTEE_GROUP_QUERY | WHEEL_GROUP_QUERY,
}

# cache group memberships for 5 minutes
AUTH_LDAP_CACHE_TIMEOUT = 300

# the Square app and location data (set to sandbox unless you want it to charge people)
SQUARE_APP_ID = '${SQUARE_APP_ID}'
SQUARE_LOCATION = '${SQUARE_LOCATION}'
SQUARE_ACCESS_TOKEN = '${SQUARE_SECRET}'

# path to the OpenDispense2 client binary
DISPENSE_BIN = '/usr/local/bin/dispense'

# path to the OpenDispense2 logfile
COKELOG_PATH = ROOT_DIR + '/cokelog'

# configure the email backend (see https://docs.djangoproject.com/en/2.1/topics/email/)
EMAIL_HOST = "secure.ucc.asn.au"
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = "uccportal"
EMAIL_HOST_PASSWORD = "${EMAIL_SECRET}"
