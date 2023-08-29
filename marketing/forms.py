from django.db import models
from django import forms


class EmailSubscribeForm(forms.Form):
    email_sub = forms.EmailField(widget=forms.TextInput(attrs={
        'class': 'form-control prepended-form-control',
        'type': 'email',
        'name': 'EMAIL',
        'placeholder': 'Your Email'
    }), label='')