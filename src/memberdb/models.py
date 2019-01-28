from django.db import models
from django.db.models import F
from django.core.validators import RegexValidator
from django.core.management.utils import get_random_string

from squarepay.dispense import get_item_price

"""
dictionary of membership types & descriptions, should be updated if these are changed in dispense.
"""
MEMBERSHIP_TYPES = {
    'oday': {
        'dispense':'pseudo:11',
        'desc':'O\' Day Special - first time members only',
        'is_guild':True,
        'is_student':True,
        'must_be_fresh':True,
    },
    'student_and_guild': {
        'dispense':'pseudo:10',
        'desc':'Student and UWA Guild member',
        'is_guild':True,
        'is_student':True,
        'must_be_fresh':False,
    },
    'student_only': {
        'dispense':'pseudo:9',
        'desc':'Student and not UWA Guild member',
        'is_guild':False,
        'is_student':True,
        'must_be_fresh':False,
    },
    'guild_only': {
        'dispense':'pseudo:8',
        'desc':'Non-Student and UWA Guild member',
        'is_guild':True,
        'is_student':False,
        'must_be_fresh':False,
    },
    'non_student': {
        'dispense':'pseudo:7',
        'desc':'Non-Student and not UWA Guild member',
        'is_guild':False,
        'is_student':False,
        'must_be_fresh':False,
    },
    'lifer': {
        'dispense':'',
        'desc':'Life member',
        'is_guild':False,
        'is_student':False,
        'must_be_fresh':False,
    }
}

def get_membership_choices(is_renew=None, get_prices=True):
    """
    turn MEMBERSHIP_TYPES into a list of choices used by Django
    also dynamically fetch the prices from dispense (if possible)
    """
    choices = []
    for key, val in MEMBERSHIP_TYPES.items():
        if (val['must_be_fresh'] and is_renew == True):
            # if you have an account already, you don't qualify for the fresher special
            continue
        if (val['dispense'] == '' and is_renew == False):
            # free memberships can only apply to life members, and they will have an existing membership somewhere
            # so this option is only displayed on the renewal form
            continue
        else:
            price = get_item_price(val['dispense'])
            if (get_prices and price is not None):
                desc = "%s ($%1.2f)" % (val['desc'], price / 100.0)
                choices += [(key, desc)]
            else:
                # don't display the price
                choices += [(key, val['desc'])]

    return choices

def get_membership_type(member):
    best = 'non_student'
    is_fresh = member.memberships.all().count() == 0
    for i, t in MEMBERSHIP_TYPES.items():
        if (t['must_be_fresh'] == is_fresh and t['is_student'] == member.is_student and t['is_guild'] == member.is_guild):
            best = i
            break
        elif (t['is_student'] == member.is_student and t['is_guild'] == member.is_guild):
            best = i
            break
    return best


def make_token():
    return get_random_string(128)

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

"""
Member table: only latest information, one record per member
Some of this data may be required by the UWA Student Guild. Other stuff is just good to know, and we don't _need_ to keep historical data for every current/past member.
Note: Privacy laws are a thing, unless people allow it then we cannot provide this info to members.
"""
class Member (IncAssocMember):
    display_name    = models.CharField ('Display name', max_length=200)
    username        = models.SlugField ('Username', max_length=32, null=False, blank=False, unique=True, validators=[RegexValidator(regex='^[a-z0-9._-]+$')])
    phone_number    = models.CharField ('Phone number', max_length=20, blank=False, validators=[RegexValidator(regex='^\+?[0-9() -]+$')])
    is_student      = models.BooleanField ('Student', default=True, blank=True, help_text="Tick this box if you are a current student at a secondary or tertiary institution in WA")
    is_guild        = models.BooleanField ('UWA Guild member', default=True, blank=True)
    id_number       = models.CharField ('Student email or Drivers License', max_length=255, blank=False, help_text="Student emails should end with '@student.*.edu.au' and drivers licences should be in the format '<AU state> 1234567'")
    member_updated  = models.DateTimeField ('Internal UCC info last updated', auto_now=True)
    login_token     = models.CharField ('Temporary access key', max_length=128, null=True, editable=False, default=make_token)

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
    membership_type = models.CharField ('Membership type', max_length=20, blank=True, null=False, choices=get_membership_choices(get_prices=False))
    payment_method  = models.CharField ('Payment method', max_length=10, blank=True, null=True, choices=PAYMENT_METHODS, default=None)
    approved        = models.BooleanField ('Membership approved', default=False)
    approver        = models.ForeignKey (Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_memberships')
    date_submitted  = models.DateTimeField ('Date signed up')
    date_paid       = models.DateTimeField ('Date of payment', blank=True, null=True)
    date_approved   = models.DateTimeField ('Date approved', blank=True, null=True)

    def __str__ (self):
        return "Member [%s] (%s) renewed membership on %s" % (self.member.username, self.member.display_name, self.date_submitted.strftime("%Y-%m-%d"))

    def get_dispense_item(self):
        return MEMBERSHIP_TYPES[self.membership_type]['dispense']

    class Meta:
        verbose_name = "Membership renewal record"
        ordering = ['approved', '-date_submitted']