from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView

from .views import MemberHomeView, MemberTokenView
from .register import RegisterView, RenewView

app_name = 'memberdb'
urlpatterns = [
    path('', MemberHomeView.as_view(), name='home'),
    path('', MemberHomeView.as_view(), name='index'),

    # use the django-provided login views with our custom templates
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),

    # override the admin login/logout views
    path('admin/login/', auth_views.LoginView.as_view(template_name='login.html')),
    path('admin/logout/', auth_views.LogoutView.as_view(template_name='logout.html')),

    # for members to "login" before having created a user account
    path('login/<username>/<member_token>/', MemberTokenView.as_view(), name='login_member'),
    
    path('register/', RegisterView.as_view(), name='register'),
    path('renew/', RenewView.as_view(), name='renew'),
    path('thanks/', TemplateView.as_view(template_name='thanks.html'), name='thanks'),
]
