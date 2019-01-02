from django.urls import path

from .views import PaymentFormView

app_name = 'squarepay'
urlpatterns = [
    path('pay/', PaymentFormView.as_view(), name='pay'),
]