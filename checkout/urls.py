from django.urls import path
from django.conf.urls import url
from .views import  OrderWizard, billing_same_as_shipping, PaymentView, FORMS

app_name = 'checkout'

urlpatterns = [
    url(r'^checkout/$', OrderWizard.as_view(FORMS, condition_dict={'billing': billing_same_as_shipping}), name='checkout_order'),
    path('payment/<str:order_nr>', PaymentView.as_view(), name='payment'),
]