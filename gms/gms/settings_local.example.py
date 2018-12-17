# Django settings for uccmemberdb project.

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = True

ADMINS = (
    ('UCC Committee', 'committee-only@ucc.asn.au'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',     # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'member.db',                        # Or path to database file if using sqlite3.
        'USER': '',                                 # Not used with sqlite3.
        'PASSWORD': '',                             # Not used with sqlite3.
        'HOST': '',                                 # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                                 # Set to empty string for default. Not used with sqlite3.
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'something-unique-here'

ALLOWED_HOSTS = []

import ldap
from django_auth_ldap.config import LDAPSearch, ActiveDirectoryGroupType, LDAPGroupQuery

AUTH_LDAP_SERVER_URI = 'ldaps://samson.ucc.gu.uwa.edu.au/'

AUTH_LDAP_GLOBAL_OPTIONS = {
    ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER,
}

# directly attempt to authenticate users to bind to LDAP
AUTH_LDAP_USER_DN_TEMPLATE = 'CN=%(user)s,CN=Users,DC=ad,DC=ucc,DC=gu,DC=uwa,DC=edu,DC=au'
AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = True

AUTH_LDAP_FIND_GROUP_PERMS = True

AUTH_LDAP_USER_SEARCH = LDAPSearch("CN=Users,DC=ad,DC=ucc,DC=gu,DC=uwa,DC=edu,DC=au",
    ldap.SCOPE_SUBTREE, "(objectClass=user)")

AUTH_LDAP_GROUP_SEARCH = LDAPSearch("OU=Groups,DC=ad,DC=ucc,DC=gu,DC=uwa,DC=edu,DC=au",
    ldap.SCOPE_SUBTREE, "(objectClass=group)")
AUTH_LDAP_GROUP_TYPE = ActiveDirectoryGroupType()

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "displayName",
    "last_name": "name"
}

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_staff": (
        LDAPGroupQuery("CN=committee,OU=Groups,DC=ad,DC=ucc,DC=gu,DC=uwa,DC=edu,DC=au") |
        LDAPGroupQuery("CN=door,OU=Groups,DC=ad,DC=ucc,DC=gu,DC=uwa,DC=edu,DC=au")
    ),
    "is_superuser": "CN=committee,OU=Groups,DC=ad,DC=ucc,DC=gu,DC=uwa,DC=edu,DC=au",
}

AUTH_LDAP_ALWAYS_UPDATE_USER = True

AUTH_LDAP_MIRROR_GROUPS = False
