from django.urls import path, include

from . import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('memberdb.urls')),
]
