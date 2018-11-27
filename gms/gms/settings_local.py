# Django settings for uccmemberdb project.

DEBUG = True

ADMINS = (
    ('UCC Committee', 'committee-only@ucc.asn.au'),
    ('David Adam', 'zanchey@ucc.gu.uwa.edu.au'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '/home/frekk/Documents/projects/usermgmt-ucc/uccportal/.db/members.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'oB8fVqxJPfeL0MomVCwExU13H3ajZd9vWFgCpL5RMuhR4JOqSXemYasppIdimhLk'

ALLOWED_HOSTS = ['secure.ucc.asn.au']
