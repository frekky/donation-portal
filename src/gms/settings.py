"""
Django settings for UCC Gumby Management System (GMS) project.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

# import local settings
from gms.settings_local import *

# DEBUG ALLOW
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', "130.95.13.36","portal.ucc.asn.au"]

# Application definition

INSTALLED_APPS = (
	'sslserver',
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'memberdb',
	'import_members',
	'squarepay',
	'formtools'
)

MIDDLEWARE = [
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'memberdb.views.MemberMiddleware',
]

ROOT_URLCONF = 'gms.urls'

WSGI_APPLICATION = 'gms.wsgi.application'

DATE_INPUT_FORMATS = ("%d-%m-%y")

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-au'

TIME_ZONE = 'Australia/Perth'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = 'memberdb:login'
LOGIN_REDIRECT_URL = 'memberdb:index'

DATABASE_ROUTERS = ['import_members.db.MemberDbRouter']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATICFILES_DIRS = [
	os.path.join(BASE_DIR, 'static'),
]
STATIC_URL = '/media/'
STATIC_ROOT = os.path.join(ROOT_DIR, 'media')

AUTHENTICATION_BACKENDS = [
	# see https://django-auth-ldap.readthedocs.io/en/latest for configuration info
	'django_auth_ldap.backend.LDAPBackend',
	'django.contrib.auth.backends.ModelBackend',
]

# see settings_local.py for LDAP settings

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [os.path.join(BASE_DIR, 'templates')],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

TEMPLATE_DEBUG = DEBUG

from django.contrib.messages import constants as message_constants
MESSAGE_LEVEL = message_constants.DEBUG

### Logging configuration ###
import logging
LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'standard': {
			'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
			'datefmt' : "%d/%b/%Y %H:%M:%S"
		},
	},
	'handlers': {
		'logfile': {
			'level': LOG_LEVEL,    
			'class':'logging.handlers.RotatingFileHandler',
			'filename': LOG_FILENAME,
			'maxBytes': 500000,
			'backupCount': 2,
			'formatter': 'standard',
		},                                     
		'console':{
			'level': LOG_LEVEL,
			'class':'logging.StreamHandler',
			'formatter': 'standard'
		},
	},
	'loggers': {
		'django': {
			'handlers':['logfile', 'console'],
			'propagate': True,
			'level': LOG_LEVEL,
		},
		'django.db.backends': {
			'handlers': ['logfile', 'console'],
			'level': LOG_LEVEL,
			'propagate': False,
		},
		'django.contrib.auth': {
			'handlers': ['logfile', 'console'],
			'level': LOG_LEVEL,
		},
		'django_auth_ldap': {
			'level': LOG_LEVEL,
			'handlers': ['logfile', 'console'],
		},
		'squarepay': {
			'level': LOG_LEVEL,
			'handlers': ['logfile', 'console'],
		}
	},
}
