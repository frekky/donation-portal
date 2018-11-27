from django.urls import path
from django.contrib import admin

admin.site.site_header = "Gumby Management System"
admin.site.site_title = "UCC Gumby Management System"
admin.site.index_title = "Membership Database"

urlpatterns = [
    path('', admin.site.urls),
]
