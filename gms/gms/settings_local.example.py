# Django settings for uccmemberdb project.

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

DEBUG = True

ADMINS = (
    ('UCC Committee', 'committee-only@ucc.asn.au'),
)

### Database connection options ###
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',     # Add 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        # this should end up in uccportal/.db/members.db
        'NAME': os.path.join(ROOT_DIR, '.db', 'members.db'),   # Or path to database file if using sqlite3.
        'USER': '',                                 # Not used with sqlite3.
        'PASSWORD': '',                             # Not used with sqlite3.
        'HOST': '',                                 # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                                 # Set to empty string for default. Not used with sqlite3.
    },
    'memberdb_old': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'uccmemberdb_2018',
        'USER': 'uccmemberdb',
        'PASSWORD': 'something-secret-here',
        'HOST': 'mussel.ucc.gu.uwa.edu.au',
        'PORT': '',
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'something-unique-here'

# Set this to whatever your ServerName/ServerAlias(es) are
ALLOWED_HOSTS = []

LOG_LEVEL = 'DEBUG'
LOG_FILENAME = os.path.join(ROOT_DIR, "django.log")

import ldap
from django_auth_ldap.config import LDAPSearch, ActiveDirectoryGroupType, LDAPGroupQuery

# this could be ad.ucc.gu.uwa.edu.au but that doesn't resolve externally -
# useful for testing, but should be changed in production so failover works
AUTH_LDAP_SERVER_URI = 'ldaps://samson.ucc.gu.uwa.edu.au/'

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