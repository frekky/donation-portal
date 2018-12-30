from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .views import MemberHomeView
from .register import RegisterView, RenewView

app_name = 'memberdb'
urlpatterns = [
    path('', MemberHomeView.as_view(), name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),

    # override the admin login/logout views
    path('admin/login/', auth_views.LoginView.as_view(template_name='login.html')),
    path('admin/logout/', auth_views.LogoutView.as_view(template_name='logout.html')),
    
    path('register/', RegisterView.as_view(), name='register'),
    path('renew/', RenewView.as_view(), name='renew'),
    path('active/', views.getactive, name='actives'),
    #path('<str:username>/', views.info, name='info'),
]