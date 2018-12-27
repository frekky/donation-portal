from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .register import RegisterView, RenewView

app_name = 'memberdb'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('renew/', RenewView.as_view(), name='renew'),
    path('home/', views.index, name='home'),
    path('active/', views.getactive, name='actives'),
    #path('<str:username>/', views.info, name='info'),
]