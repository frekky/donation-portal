from django.urls import path

from .views import PaymentFormView

# note that other apps (like memberdb) may have dependencies via the reverse URL
# using something like reverse('squarepay:pay_membership', ...)

app_name = 'squarepay'
urlpatterns = [
    path('pay/<int:pk>/', PaymentFormView.as_view(), name='donate'),
]
