from django.contrib.admin import *

"""
Here we define our own customised admin interface
"""
class MemberDbAdmin(AdminSite):
    site_header = "Gumby Management System"
    site_title = "UCC Gumby Management System"
    index_title = "Membership Database"

    """
    Make sure we register the default admin site things as well
    from https://stackoverflow.com/questions/32612400/auto-register-django-auth-models-using-custom-admin-site
    """
    def __init__(self, *args, **kwargs):
        super(MemberDbAdmin, self).__init__(*args, **kwargs)
        self._registry.update(site._registry)

site = MemberDbAdmin()