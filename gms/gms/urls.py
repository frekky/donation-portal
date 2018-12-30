from django.urls import path, include

from . import admin

urlpatterns = [
    path('', include('memberdb.urls')),
    path('admin/', admin.site.urls),
]
