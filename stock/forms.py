from django import forms
from .models import SIZE_LABEL

AMOUNT = (
    ('1', 1),
    ('2', 2),
    ('3', 3),
    ('4', 4),
    ('5', 5),
)

class CosmeticOrderForm(forms.Form):
    amount = forms.ChoiceField(
        widget=forms.Select(attrs={
            'class': 'custom-select',
            'id': 'product-size',
        }), choices=AMOUNT)


class ProductOrderForm(forms.Form):
    size = forms.ChoiceField(
        widget=forms.Select(attrs={
            'class': 'custom-select',
            'id': 'product-size',
        }), choices=SIZE_LABEL)
    color = forms.CharField(widget=forms.TextInput(attrs={
        'type': 'hidden'
    }),
        initial='')
    amount = forms.ChoiceField(
        widget=forms.Select(attrs={
            'class': 'custom-select',
            'id': 'product-size',
        }), choices=AMOUNT)

    def __init__(self, *args, **kwargs):
        super(ProductOrderForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            initials = kwargs.pop('initial')
            sizes_choices = [("", "please choose a size"), ] + \
                list(initials.get('sizes').items())
            color_choice = initials.get('color')
            self.fields['size'].choices = sizes_choices
            self.fields['color'].initial = color_choice


class ProductSubscription(forms.Form):
    email_input = forms.EmailField(widget=forms.TextInput(attrs={
        'class': 'form-control prepended-form-control',
        'type': 'email',
        'name': 'EMAIL',
        'placeholder': 'Your Email'
    }), label='Stay Informed')
