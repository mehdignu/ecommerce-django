from django.urls import path

from .views import email_list_subscribe

app_name = 'marketing'

urlpatterns = [
    path('subscribe/', email_list_subscribe, name='subscribe'),
]