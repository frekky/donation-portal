from django.urls import path, include
from django.contrib import admin

urlpatterns = [
#    path('', include('donationtracker.urls')),
    path('admin/', admin.site.urls),
    path('payment/', include('squarepay.urls')),
]
