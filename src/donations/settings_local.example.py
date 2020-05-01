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
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = '${APP_SECRET}'

# Set this to whatever your ServerName/ServerAlias(es) are
ALLOWED_HOSTS = ['${DEPLOY_HOST}']

LOG_LEVEL = 'DEBUG'
LOG_LEVEL_DJANGO = 'WARNING'
LOG_FILENAME = os.path.join(ROOT_DIR, "django.log")

# the Square app and location data (set to sandbox unless you want it to charge people)
SQUARE_APP_ID = '${SQUARE_APP_ID}'
SQUARE_LOCATION = '${SQUARE_LOCATION}'
SQUARE_ACCESS_TOKEN = '${SQUARE_SECRET}'
