from django.db import models
from django.db.models import F
from django.core.validators import RegexValidator

"""
dictionary of membership types & descriptions, should be updated if these are changed in dispense.
"""
MEMBERSHIP_TYPES_ = [
    {
        'dispense':'pseudo:11',
        'desc':'O\' Day Special',
        'is_guild':True,
        'is_student':True,
        'must_be_fresh':True,
    },
    {
        'dispense':'pseudo:10',
        'desc':'Student and UWA Guild member',
        'is_guild':True,
        'is_student':True,
        'must_be_fresh':False,
    },
    {
        'dispense':'pseudo:9',
        'desc':'Student and not UWA Guild member',
        'is_guild':False,
        'is_student':True,
        'must_be_fresh':False,
    },
    {
        'dispense':'pseudo:8',
        'desc':'Non-Student and UWA Guild member',
        'is_guild':True,
        'is_student':False,
        'must_be_fresh':False,
    },
    {
        'dispense':'pseudo:7',
        'desc':'Non-Student and not UWA Guild member',
        'is_guild':False,
        'is_student':False,
        'must_be_fresh':False,
    },
    {
        'dispense':'',
        'desc':'Life member',
        'is_guild':False,
        'is_student':False,
        'must_be_fresh':False,
    }
]

def get_membership_types():
    l = []
    for t in MEMBERSHIP_TYPES_:
        l += [(t['dispense'], t['desc'])]
    return l

MEMBERSHIP_TYPES = get_membership_types()

PAYMENT_METHODS = [
    ('dispense', 'Existing dispense credit'),
    ('cash', 'Cash (in person)'),
    ('card', 'Tap-n-Go via Square (in person)'),
    ('online', 'Online payment via Square'),
    ('eft', 'Bank transfer'),
    ('', 'No payment')
]

"""
Member record for data we are legally required to keep under Incorporations Act (and make available to members upon request)
Note: these data should only be changed administratively or with suitable validation since it must be up to date & accurate.
"""
class IncAssocMember (models.Model):
    first_name      = models.CharField ('First name', max_length=200)
    last_name       = models.CharField ('Surname', max_length=200)
    email_address   = models.EmailField ('Email address', blank=False)
    updated         = models.DateTimeField ('IncA. info last updated', auto_now=True)
    created         = models.DateTimeField ('When created', auto_now_add=True)

    def __str__ (self):
        return "%s %s <%s>" % (self.first_name, self.last_name, self.email_address)
    
    class Meta:
        verbose_name = "Incorporations Act member data"
        verbose_name_plural = verbose_name
        default_permissions = ['view']

"""
Member table: only latest information, one record per member
Some of this data may be required by the UWA Student Guild. Other stuff is just good to know, and we don't _need_ to keep historical data for every current/past member.
Note: Privacy laws are a thing, unless people allow it then we cannot provide this info to members.
"""
class Member (IncAssocMember):
    display_name    = models.CharField ('Display name', max_length=200)
    username        = models.SlugField ('Username', max_length=32, blank=False, unique=True, validators=[RegexValidator(regex='^[a-z0-9._-]+$')])
    phone_number    = models.CharField ('Phone number', max_length=20, blank=False, validators=[RegexValidator(regex='^\+?[0-9() -]+$')])
    is_student      = models.BooleanField ('Student at UWA', default=True, blank=True)
    is_guild        = models.BooleanField ('UWA Guild member', default=True, blank=True)
    id_number       = models.CharField ('Student number or Drivers License', max_length=50 , blank=False)
    member_updated  = models.DateTimeField ('Internal UCC info last updated', auto_now=True)

    def __str__ (self):
        if (self.display_name != "%s %s" % (self.first_name, self.last_name)):
            name = "%s (%s %s)" % (self.display_name, self.first_name, self.last_name)
        else:
            name = self.display_name
        return "[%s] %s" % (self.username, name)

    class Meta:
        verbose_name = "Internal UCC member record"

"""
Membership table: store information related to individual (successful/accepted) signups/renewals
"""
class Membership (models.Model):
    member          = models.ForeignKey (Member, on_delete=models.CASCADE, related_name='memberships')
    membership_type = models.CharField ('Membership type', max_length=10, blank=True, null=False, choices=MEMBERSHIP_TYPES)
    payment_method  = models.CharField ('Payment method', max_length=10, blank=True, null=True, choices=PAYMENT_METHODS, default=None)
    approved        = models.BooleanField ('Membership approved', default=False)
    approver        = models.ForeignKey (Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_memberships')
    date_submitted  = models.DateTimeField ('Date signed up')
    date_paid       = models.DateTimeField ('Date of payment', blank=True, null=True)
    date_approved   = models.DateTimeField ('Date approved', blank=True, null=True)

    def __str__ (self):
        return "Member [%s] (%s) renewed membership on %s" % (self.member.username, self.member.display_name, self.date_submitted.strftime("%Y-%m-%d"))

    class Meta:
        verbose_name = "Membership renewal record"
        ordering = ['approved', '-date_submitted']