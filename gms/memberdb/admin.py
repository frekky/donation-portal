from django.contrib import admin
from memberdb.models import Member, IncAssocMember, Membership
from memberdb.actions import download_as_csv 

admin.site.site_header = "Gumby Management System"
admin.site.site_title = "UCC Gumby Management System"
admin.site.index_title = "Membership Database"

"""
Customise the administrative interface for modifying Member records
"""
class MemberAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'display_name', 'username']
    list_filter = ['is_guild', 'is_student']
    search_fields = list_display
    actions = [download_as_csv]

admin.site.register(Member, MemberAdmin)

# Register the other models with default admin site pages
admin.site.register(IncAssocMember)
admin.site.register(Membership)
