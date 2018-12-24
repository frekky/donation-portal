from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from gms import admin

from memberdb.models import Member, IncAssocMember, Membership
from memberdb.actions import download_as_csv
from memberdb.approve import MembershipApprovalForm, MembershipApprovalAdminView


def get_model_url(pk, model_name):
    return reverse('admin:memberdb_%s_change' % model_name, args=[pk])

"""
helper mixin to make the admin page display only "View" rather than "Change" or "Add"
"""
class ReadOnlyModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False
        
    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

"""
This makes use of some hacky javascript to replace the default "actions" dropdown list with more user-friendly buttons for each action.
"""
class ButtonActionModelAdmin(admin.ModelAdmin):
    class Media:
        js = ['action_buttons.js']

"""
Define the administrative interface for viewing member details required under the Incorporations Act
"""
class IAMemberAdmin(ButtonActionModelAdmin, ReadOnlyModelAdmin):
    readonly_fields = ['__str__', 'updated', 'created']
    fields = ['first_name', 'last_name', 'email_address', 'updated', 'created']
    search_fields = ['first_name', 'last_name', 'email_address']
    list_display = readonly_fields
    actions = [download_as_csv]

    # add a "go to member" URL into the template context data
    def change_view(self, request, object_id, form_url='', extra_context={}):
        extra_context['member_edit_url'] = get_model_url(object_id, 'member')
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
        
class MembershipInline(admin.TabularInline):
    model = Membership
    readonly_fields = ['member', 'date_submitted']
    radio_fields = {'payment_method': admin.VERTICAL, 'membership_type': admin.VERTICAL}
    extra = 0
    fk_name = 'member'

class MemberAdmin(ButtonActionModelAdmin):
    list_display = ['first_name', 'last_name', 'display_name', 'username']
    list_filter = ['is_guild', 'is_student']
    readonly_fields = ['member_updated', 'updated', 'created']
    search_fields = list_display
    actions = [download_as_csv]
    inlines = [MembershipInline]

    # add a "go to member" URL into the template context data
    def change_view(self, request, object_id, form_url='', extra_context={}):
        extra_context['incassocmember_url'] = get_model_url(object_id, 'incassocmember')
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

"""
Define the admin page for viewing normal Member records (all details included) and approving them
"""
class MembershipAdmin(ButtonActionModelAdmin):
    list_display = ['membership_info', 'membership_type', 'payment_method', 'approved', 'date_submitted', 'member_actions']
    list_display_links = None
    list_filter = ['approved']
    readonly_fields = ['date_submitted']
    radio_fields = {'payment_method': admin.VERTICAL, 'membership_type': admin.VERTICAL}

    # make the admin page queryset preload the parent records (Member) 
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('member')

    # add custom URLs to this model in the admin site
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<object_id>/approve/', self.admin_site.admin_view(self.process_approve), name='membership-approve'),
        ]
        return custom_urls + urls

    # display a short summary of relevant member / membership info for pending memberships
    def membership_info(self, ms):
        context = {
            'ms': ms,
            'member': ms.member,
            'member_url': get_model_url(ms.member.pk, 'member'),
        }
        html = render_to_string('admin/memberdb/membership_summary.html', context)
        return mark_safe(html)
    
    membership_info.short_description = 'Membership info'
    membership_info.allow_tags = True

    # called per record, returns HTML to display under the "Actions" column
    def member_actions(self, ms):
        context = {
            'ms': ms,
            'member': ms.member,
            'member_url': get_model_url(ms.member.pk, 'member'),
            'member_approve': reverse('admin:membership-approve', args=[ms.pk])
        }
        html = render_to_string('admin/memberdb/membership_actions.html', context)
        return mark_safe(html)

    member_actions.short_description = 'Actions'
    member_actions.allow_tags = True

    def process_approve(self, request, *args, **kwargs):
        #breakpoint();
        #member = self.get_object(request, member_id)
        #return MembershipApprovalAdminView.as_view(member=member, admin=self)(request, *args, **kwargs)
        return MembershipApprovalAdminView.as_view(admin=self)(request, *args, **kwargs)
        """
        if request.method != 'POST':
            form = MembershipApprovalForm(instance=member)
        else:
            form = MembershipApprovalForm(request.POST, instance=member)
            if form.is_valid():
                form.save()

                self.message_user(request, 'Approve success')
                url = reverse(
                    'admin:memberdb_member_change',
                    args=[member.pk],
                    current_app=self.admin_site.name,
                )
                return HttpResponseRedirect(url)

        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['member'] = member
        context['form'] = form

        return render(request, 'admin/memberdb/membership_approve.html', context)
        """

# Register the other models with either default admin site pages or with optional customisations
admin.site.register(Member, MemberAdmin)
admin.site.register(IncAssocMember, IAMemberAdmin)
admin.site.register(Membership, MembershipAdmin)