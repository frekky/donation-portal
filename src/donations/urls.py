from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

from donationtracker.views import leaderboard, RegisterView

urlpatterns = [
#    path('', include('donationtracker.urls')),
    path('', leaderboard, name='leaderboard'),

    # use the django-provided login views with our custom templates
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),

    path('register/', RegisterView.as_view(), name='register'),

    path('admin/', admin.site.urls),
    path('payment/', include('squarepay.urls')),
]
