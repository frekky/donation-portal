from django.conf.urls import include, url
from django.contrib import admin

admin.site.site_header = "Gumby Management System"
admin.site.site_title = "UCC Gumby Management System"
admin.site.index_title = "Membership Database"

urlpatterns = (
    # Examples:
    # url(r'^$', 'gms.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^', include(admin.site.urls)),
)
