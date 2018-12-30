from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from .models import OldMember
from memberdb.models import Member

def import_old_member(modeladmin, request, queryset):
    """
    admin action: Import the selected OldMember records into the new MemberDB format
    don't overwrite records if they already exist (matching by username)
    """
    num_success = 0
    total = queryset.count()
    for om in queryset:
        try:
            # create a new Member object
            nm = Member(username=om.username)

            # fudge the data as much as we can, people will have to renew memberships and check this anyway
            nm.first_name, nm.last_name = om.real_name.split(" ", 1)
            nm.display_name = om.real_name
            nm.is_guild = om.guild_member
            nm.phone_number = om.phone_number
            nm.id_number = om.student_no
            nm.email_address = om.email_address
            if (om.membership_type == 1 or om.membership_type == 2): # O'day special or student
                nm.is_student = True
            else:
                nm.is_student = False
        
            if (nm.username == '' or nm.username is None):
                raise ValidationError("username cannot be blank")
            nm.save()
            num_success += 1
        except BaseException as e:
            modeladmin.message_user(request, 'Could not import record (%s): %s' % (om, e), level=messages.ERROR)
        
    if (num_success > 0):
        modeladmin.message_user(request, 'Successfully imported %d of %d records.' % (num_success, total))

import_old_member.short_description = "Import selected records to new MemberDB"