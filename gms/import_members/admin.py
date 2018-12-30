from django.db.models import Q
from gms import admin
from memberdb.actions import download_as_csv

from .models import OldMember
from .actions import import_old_member

class UsernameNullListFilter(admin.SimpleListFilter):
    """
    see https://docs.djangoproject.com/en/2.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter
    """
    title = 'membership type'
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        return (
            ('fresh', 'first time member (blank username)'),
            ('stale', 'recurring member'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        fresh = Q(username__isnull=True) | Q(username__exact='')
        if self.value() == 'fresh':
            return queryset.filter(fresh)
        if self.value() == 'stale':
            return queryset.filter(~fresh)


class MemberAdmin(admin.ModelAdmin):
    list_display = ('real_name', 'username', 'membership_type', 'guild_member')
    list_filter = ['guild_member', UsernameNullListFilter, 'membership_type']
    search_fields = ('real_name', 'username', )
    actions = [download_as_csv, import_old_member]

# Register your models here.
admin.site.register(OldMember, MemberAdmin)