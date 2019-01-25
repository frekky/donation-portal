from django.db import models

import datetime
                               
MEMBERSHIP_TYPES = (                       
    (1, 'O\' Day Special'),                                           
    (2, 'Student'),
    (3, 'Non Student'),                  
)

class OldMember (models.Model):
    real_name       = models.CharField ('Real Name', max_length=200,)
    username        = models.CharField ('Username', max_length=16, blank=True)
    email_address   = models.CharField ('Email Address', max_length=200, blank=True)
    membership_type = models.IntegerField ('Membership Type', choices=MEMBERSHIP_TYPES,)
    guild_member    = models.BooleanField ('Guild Member', default=False, blank=True)
    student_no      = models.CharField ('Student Number or ID Number', max_length=20, blank=True)
    phone_number    = models.CharField ('Phone Number', max_length=14, blank=True)
    date_of_birth   = models.DateField ('Date of Birth', null=True, blank=True)
    signed_up       = models.DateField ('Signed up')

    def __str__(self):
        if len (self.username) > 0:
            return "%s [%s]" % (self.real_name, self.username)
        else:
            return self.real_name

    class Meta:
        managed = False
        db_table = 'memberdb_member'
        verbose_name = 'Old member record'