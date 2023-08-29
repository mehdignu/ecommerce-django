from django.db import models
from stock.models import Product, Color, Size
from order.models import Order
from checkout.utils import get_email_infos, confirm_with_email
from django.utils.html import format_html
from .forms import SHIPPING_PRICES, SHIPPING_OPTION


class Customer(models.Model):
    ''' Customer Profile '''
    first_name_c = models.CharField(max_length=40)
    last_name_c = models.CharField(max_length=40)
    phone_c = models.CharField(max_length=40)
    email_c = models.CharField(max_length=40)
    address_c = models.CharField(max_length=100)
    street_c = models.CharField(max_length=100)
    city_c = models.CharField(max_length=100)
    region_c = models.CharField(max_length=100)
    zip_c = models.CharField(max_length=100)
    fax_c = models.CharField(max_length=100)
    session_key_c = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name_c} {self.last_name_c}"


class Shipping(models.Model):
    ''' Order shipping details '''
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    telephone = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)
    fax = models.CharField(max_length=100)
    same_billing_address = models.BooleanField()

    def __str__(self):
        return f"{self.address}, {self.street}, {self.city}, {self.region}, {self.zip}, {self.country}"



class Billing(models.Model):
    ''' Order Billing details '''
    first_name_b = models.CharField(max_length=100)
    last_name_b = models.CharField(max_length=100)
    telephone_b = models.CharField(max_length=100)
    company_b = models.CharField(max_length=100)
    country_b = models.CharField(max_length=100)
    address_b = models.CharField(max_length=100)
    street_b = models.CharField(max_length=100)
    city_b = models.CharField(max_length=100)
    region_b = models.CharField(max_length=100)
    zip_b = models.CharField(max_length=100)
    fax_b = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.address_b}, {self.street_b}, {self.city_b}, {self.region_b}, {self.zip_b}, {self.country_b}"


class CheckoutModel(models.Model):
    ''' final model to save the user infos and orders '''
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    shiping_infos = models.ForeignKey(Shipping, on_delete=models.DO_NOTHING)
    billing_infos = models.ForeignKey(
        Billing, null=True, on_delete=models.DO_NOTHING)
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING)
    shipping_method = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    checkout_date = models.DateTimeField()
    delivered = models.BooleanField(default=False)

    def __str__(self):
        return self.customer.first_name_c

    def products_details(self):
        order_details = '<ul>'
        for p in self.order.products.all():
            price = 0
            if p.product.discount_price:
                price = p.product.discount_price * p.quantity
            else:
                price = p.product.price * p.quantity

            order_details += '<li>' + str(p.quantity) + ' of ' + p.product.title + ' ('+ str(price) +' TND)' +'</li>'
        order_details += '</ul>'
        return format_html(order_details)

    def products_sum(self):
        order_sum = 0
        for p in self.order.products.all():
            price = 0
            if p.product.discount_price:
                price = p.product.discount_price * p.quantity
            else:
                price = p.product.price * p.quantity
            order_sum += price

        shipping_price = 0
        if self.shipping_method in dict(SHIPPING_PRICES):
            shipping_price = dict(SHIPPING_PRICES)[self.shipping_method]
        total_price = order_sum + shipping_price

        return str(total_price) + ' TND'

    def customer_contact(self):
        return self.customer.phone_c
    
    def shipping_details(self):
        shipping_price = 0
        shipping_value = ''
        if self.shipping_method in dict(SHIPPING_PRICES):
            shipping_price = dict(SHIPPING_PRICES)[self.shipping_method]
            shipping_value = dict(SHIPPING_OPTION)[self.shipping_method]
        return shipping_value + ' ('+ str(shipping_price) + ' TND)'



    def save(self, *args, **kwargs):
          # Compare old vs new
        if self.id:
            checkout_model = CheckoutModel.objects.values(
                'delivered').get(id=self.id)
            if checkout_model['delivered'] != self.delivered and self.delivered == True:
                # send email confirmation of delivery
                msg_html, email_address = get_email_infos(self, True)
                confirm_with_email.delay(msg_html, email_address)
            if self.delivered == False and checkout_model['delivered'] == True:
                self.delivered = True
        super().save(*args, **kwargs)
