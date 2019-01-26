from django.urls import path

from .views import PaymentFormView, MembershipPaymentView

# note that other apps (like memberdb) may have dependencies via the reverse URL
# using something like reverse('squarepay:pay_membership', ...)

app_name = 'squarepay'
urlpatterns = [
    path('pay/<int:pk>/', MembershipPaymentView.as_view(), name='pay_membership'),
]
