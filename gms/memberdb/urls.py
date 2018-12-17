from django.urls import path

from . import views
from .register import RegisterView

app_name = 'memberdb'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', RegisterView.as_view(), name='register'),
    path('renew/', views.renew, name='renew'),
    path('renew/<str:username>/', views.renew, name='renew'),
    path('<str:username>/', views.info, name='info'),
]