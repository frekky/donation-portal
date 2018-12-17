from django.db import models
from django.core.validators import RegexValidator
import datetime

MEMBERSHIP_TYPES = [
    ('pseudo:11', 'O\' Day Special'),
    ('pseudo:10', 'Student and UWA Guild member'),
    ('pseudo:9', 'Student and not UWA Guild member'),
    ('pseudo:8', 'Non-Student and UWA Guild member'),
    ('pseudo:7', 'Non-Student and not UWA Guild member'),
    ('', 'Life member'),
]

PAYMENT_METHODS = [
    ('dispense', 'Existing dispense credit'),
    ('cash', 'Cash (in person)'),
    ('card', 'Tap-n-Go via Square (in person)'),
    ('online', 'Online payment via Square'),
    ('eft', 'Bank transfer')
]

"""
Member record for data we are legally required to keep under Incorporations Act (and make available to members upon request)
Note: these data should only be changed administratively or with suitable validation since it must be up to date & accurate.
"""
class IncAssocMember (models.Model):
    first_name      = models.CharField ('First name', max_length=200)
    last_name       = models.CharField ('Surname', max_length=200)
    email_address   = models.EmailField ('Email address', blank=True)
    updated         = models.DateField ('Last updated', auto_now=True)
    created         = models.DateField ('When created', auto_now_add=True)
    def __unicode__ (self):
        return "%s %s <%s>" % (self.first_name, self.last_name, self.email_address)


"""
Member table: only latest information, one record per member
Some of this data may be required by the UWA Student Guild. Other stuff is just good to know, and we don't _need_ to keep historical data for every current/past member.
Note: Privacy laws are a thing, unless people allow it then we cannot provide this info to members.
"""
class Member (IncAssocMember):
    display_name    = models.CharField ('Display name', max_length=200)
    username        = models.SlugField ('Username', max_length=32, blank=False, unique=True, validators=[RegexValidator(regex='^[a-z0-9._-]+$')])
    phone_number    = models.CharField ('Phone number', max_length=20, blank=False, validators=[RegexValidator(regex='^\+?[0-9() -]+$')])
    last_renew      = models.DateField ('Last renewal', blank=True, null=True)
    is_student      = models.BooleanField ('Student at UWA', default=True, blank=True)
    is_guild        = models.BooleanField ('UWA Guild member', default=True, blank=True)
    id_number       = models.CharField ('Student number or Drivers License', max_length=50 , blank=False)
    member_updated  = models.DateField ('Last updated', auto_now=True)
    def __unicode__ (self):
        if (self.display_name != "%s %s" % (self.first_name, self.last_name)):
            name = "%s (%s %s)" % (self.display_name, self.first_name, self.last_name)
        else:
            name = self.display_name
        return "[%s] %s" % (self.username, name)

"""
Membership table: store information related to individual (successful/accepted) signups/renewals
"""
class Membership (models.Model):
    member          = models.ForeignKey (Member, on_delete=models.CASCADE)
    membership_type = models.CharField ('Membership type', max_length=10, blank=False, null=True)
    payment_method  = models.CharField ('Payment method', max_length=10, choices=PAYMENT_METHODS)
    accepted        = models.BooleanField ('Membership approved', default=False)
    date_submitted  = models.DateTimeField ('Date signed up', auto_now_add=True)
    date_paid       = models.DateTimeField ('Date of payment', blank=True, null=True)
    date_accepted   = models.DateTimeField ('Date approved', blank=True, null=True)
