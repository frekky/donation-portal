from django.urls import path

from .views import PaymentFormView, MembershipPaymentView

app_name = 'squarepay'
urlpatterns = [
    path('pay/<int:pk>/<str:token>/', MembershipPaymentView.as_view(), name='pay'),
]
