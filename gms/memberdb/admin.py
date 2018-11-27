from django.contrib import admin
from memberdb.models import Member
from memberdb.actions import download_as_csv 

class MemberAdmin(admin.ModelAdmin):
    list_display = ('real_name', 'username', 'guild_member')
    list_filter = ['guild_member', 'membership_type']
    search_fields = ('real_name', 'username', )
    actions = [download_as_csv]

admin.site.register(Member, MemberAdmin)
