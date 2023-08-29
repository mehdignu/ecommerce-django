from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.conf import settings
from .forms import EmailSubscribeForm
from .models import Subscriptions
import requests
import json


MAILCHIMP_API_KEY = settings.MAILCHIMP_API_KEY
MAILCHIMP_DATA_CENTER = settings.MAILCHIMP_DATA_CENTER
MAILCHIMP_EMAIL_LIST_ID = settings.MAILCHIMP_EMAIL_LIST_ID

api_url = f'https://{MAILCHIMP_DATA_CENTER}.api.mailchimp.com/3.0/'
members_endpoint = f'{api_url}/lists/{MAILCHIMP_EMAIL_LIST_ID}/members'


def subscribe(email):
    ''' subscribe a user to mailchimp '''
    data = {
        "email_address": email,
        "status": "subscribed",
    }

    r = requests.post(
        members_endpoint,
        auth=("", MAILCHIMP_API_KEY),
        data=json.dumps(data)
    )
    # save the email to the database
    Subscriptions.objects.create(email=email)

    return r.status_code, r.json()


@require_http_methods(["POST"])
def email_list_subscribe(request):
    form = EmailSubscribeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data.get('email_sub')
            message_alert = {}
            email_sub_qs = Subscriptions.objects.filter(email=email)
            if email_sub_qs.exists():
                # return message that user already subscribed
                message_alert = {
                    'message': 'already registered!',
                    'sub_message': 'Your E-mail address is already registered with us!',
                    'message_tag': 'success',
                    'message_icon': 'czi-check-circle'
                }
            else:
                status_code, val = subscribe(email)
                message_alert = {
                    'message': 'successfully registered!',
                    'sub_message': 'Your E-mail address is successfully registered with us!',
                    'message_tag': 'success',
                    'message_icon': 'czi-check-circle'
                }
            if request.session.session_key:
                request.session['message_alert'] = message_alert
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
