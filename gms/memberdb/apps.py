from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig

class MemberConfig(AppConfig):
    name = 'memberdb'
    label = name
    verbose_name = "UCC Member Database"

class MemberDbAdminConfig(AdminConfig):
    default_site = 'memberdb.admin.MemberDbAdmin'
