from django import forms


COUNTRY = (
    ('Tunisia', 'Tunisia'),
)

SHIPPING_OPTION = (
    ('TNE', 'Tunisia Express'),
)

SHIPPING_PRICES = (
    ('TNE', 7),
)

PAYMENT_OPTION = (
    ('edinar', 'E-Dinar'),
    ('cbn', 'Carte Bancaire Nationale')
)


class OrderDetails(forms.Form):

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'checkout-fn'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'checkout-ln'
    }))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'type': 'email',
        'id': 'checkout-email'
    }))
    telephone = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'checkout-phone'
    }))
    company = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'checkout-company'
    }), required=False)
    country = forms.ChoiceField(widget=forms.Select(attrs={
        'class': 'form-control custom-select',
        'id': 'checkout-country'

    }), choices=COUNTRY)
    address = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'checkout-address'
    }))
    street = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'checkout-street'
    }), required=False)
    city = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'checkout-city'
    }))
    region = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'checkout-region'
    }))
    zip = forms.CharField(widget=forms.TextInput({
        'class': 'form-control',
        'id': 'checkout-zip'
    }))
    fax = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'checkout-fax'
    }), required=False)
    same_billing_address = forms.BooleanField(widget=forms.CheckboxInput(attrs={
        'class': 'custom-control-input',
        'id': 'same-address',
        'checked': 'checked'
    }), required=False)



class BillingDetails(forms.Form):

    first_name_b = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'checkout-fn'
    }))
    last_name_b = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'checkout-ln'
    }))

    telephone_b = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'checkout-phone'
    }))
    company_b = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'checkout-company'
    }), required=False)
    country_b = forms.ChoiceField(widget=forms.Select(attrs={
        'class': 'form-control custom-select',
        'id': 'checkout-country'

    }), choices=COUNTRY)
    address_b = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'checkout-address'
    }))
    street_b = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'checkout-street'
    }), required=False)
    city_b = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'checkout-city'
    }))
    region_b = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'checkout-region'
    }))
    zip_b = forms.CharField(widget=forms.TextInput({
        'class': 'form-control',
        'id': 'checkout-zip'
    }))
    fax_b = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'checkout-fax'
    }), required=False)


class ShippingDetails(forms.Form):
    shipping_method = forms.ChoiceField(widget=forms.RadioSelect(), choices=SHIPPING_OPTION)

class PaymentDetails(forms.Form):
    payment_method = forms.ChoiceField(widget=forms.RadioSelect(), choices=PAYMENT_OPTION)

class ReviewDetails(forms.Form):
    recapatcha = forms.CharField(widget=forms.TextInput(attrs={
        'type': 'hidden',
        'name': 'g-recaptcha-response',
        'id': 'recaptcha'
    }))
