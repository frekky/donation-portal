from django.urls import path

from . import views

app_name = 'memberdb'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('renew/', views.renew, name='renew'),
    path('renew/<str:username>/', views.renew, name='renew'),
    path('<str:username>/', views.info, name='info'),
]