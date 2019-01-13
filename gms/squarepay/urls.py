from django.urls import path

from .views import PaymentFormView

app_name = 'squarepay'
urlpatterns = [
    path('pay/<int:pk>/<str:token>/', PaymentFormView.as_view(), name='pay'),
]