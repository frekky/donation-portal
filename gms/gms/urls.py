from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('', include('memberdb.urls')),
    path('admin/', admin.site.urls),
]
