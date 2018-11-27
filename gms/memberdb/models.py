from django.db import models
import datetime

MEMBERSHIP_TYPES = (
	(1, 'O\' Day Special'),
	(2, 'Student'),
	(3, 'Non Student'),
#	(1, 'O\' Day Special'),
#	(2, 'First time UWA student'),
#	(3, 'Rejoining UWA student'),
#	(4, 'Not a student'),
#	(5, 'Member of an associate club'),
#	(6, 'Student at another univeristy'),
#	(7, 'Life member'),
)

#GENDERS = (
#	(1, 'Male'),
#	(2, 'Female'),
#	(3, 'Other'),
#	(4, 'Undefined'),
#)

class Member (models.Model):
	#membership_year = models.IntegerField ('Membership Year', default=datetime.date.today().year,)
	real_name	= models.CharField ('Real Name', max_length=200,)
	username	= models.CharField ('Username', max_length=16, blank=True)
	email_address   = models.CharField ('Email Address', max_length=200,
				blank=True)
	membership_type	= models.IntegerField ('Membership Type', choices=MEMBERSHIP_TYPES,)
	guild_member	= models.BooleanField ('Guild Member', 
				default=False, blank=True)
	student_no      = models.CharField ('Student Number or ID Number', max_length=20,
				blank=True)
	phone_number	= models.CharField ('Phone Number', max_length=14,
				blank=True)
	date_of_birth	= models.DateField ('Date of Birth', null=True, blank=True)
	signed_up	= models.DateField ('Signed up', default=datetime.date.today())
	
	def __unicode__ (self):
		if len (self.username) > 0:
			return "%s <%s>" % (self.real_name, self.username)
		else:
			return self.real_name

