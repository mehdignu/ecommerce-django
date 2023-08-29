from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import View
from order.models import Order
from .forms import OrderDetails, BillingDetails, ShippingDetails, PaymentDetails, ReviewDetails, SHIPPING_PRICES, SHIPPING_OPTION, PAYMENT_OPTION
from formtools.wizard.views import SessionWizardView
from .models import Shipping, Billing, Customer, CheckoutModel
from datetime import datetime, timedelta, timezone
from .utils import confirm_with_email, get_email_infos
from django.conf import settings
from marketing.views import subscribe
import requests

FORMS = [("checkout", OrderDetails),
         ("billing", BillingDetails),
         ("shipping", ShippingDetails),
         ("payment", PaymentDetails),
         ("review", ReviewDetails)
         ]

TEMPLATES = {"checkout": "pages/checkout/checkout.html",
             "billing": "pages/checkout/billing.html",
             "shipping": "pages/checkout/shipping_choice.html",
             "payment": "pages/checkout/payment_choice.html",
             "review": "pages/checkout/review_order.html"
             }


def billing_same_as_shipping(wizard):
    # try to get the cleaned data of step 1
    cleaned_data = wizard.get_cleaned_data_for_step('checkout') or {}
    # check if the field ``leave_message`` was checked.
    return not cleaned_data.get('same_billing_address', True)


class OrderWizard(SessionWizardView):
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super(OrderWizard, self).get_context_data(
            form=form, **kwargs)
        session_id = self.request.session.session_key
        shipping = ''
        shipping_value = ''
        shipping_price = 0
        total_sum = 0
        prices = {}
        if self.steps.current != 'checkout' or self.steps.current != 'billing':
            shipping_data = self.storage.get_step_data('shipping')
            if shipping_data:
                shipping = shipping_data.get('shipping-shipping_method', '')
                shipping_value = dict(SHIPPING_OPTION)[shipping]
                if len(shipping) != 0:
                    shipping_price = dict(SHIPPING_PRICES)[shipping]
                    prices['shipping_price'] = shipping_price
        order_products = get_order(session_id)
        if order_products is None:
            return redirect("pages:index")
        products_total_sum = order_products.get_total_sum()
        prices['products_total_sum'] = products_total_sum
        total_sum = products_total_sum
        if shipping_price != 0:
            total_sum += shipping_price
        prices['total_sum'] = total_sum

        review_data = {}
        if self.steps.current == 'review':
            order_details = self.storage.get_step_data('checkout')
            payment_details = self.storage.get_step_data('payment')
            review_data['customer'] = order_details.get(
                'checkout-first_name', '') + ' ' + order_details.get('checkout-last_name', '')
            review_data['phone'] = order_details.get('checkout-telephone')
            review_data['address'] = order_details.get('checkout-address')
            payment_key = payment_details.get(
                'payment-payment_method')
            payment_value = dict(PAYMENT_OPTION)[payment_key]
            review_data['payment'] = payment_value

        context.update({'order_products': order_products, 'shipping': shipping_value,
                        'prices': prices, 'review_data': review_data, 'checkout': True, 'site_key': settings.RECAPTCHA_SITE_KEY})
        return context

    def render_to_response(self, context, **response_kwargs):
        # check if the users cart contains products
        order_products = get_order(self.request.session.session_key)
        if order_products == None:
            return redirect("pages:index")

        # limit the users orders to 3 times per day
        session_id = self.request.session.session_key
        users_orders = Order.objects.filter(
            session_key=session_id, ordered=True).values('ordered_date').all()
        same_day = False
        same_day_counter = 0
        if users_orders.exists():
            for users_order_date in users_orders:
                users_date = users_order_date.get('ordered_date')
                date_now = datetime.now(timezone.utc)
                date_diff = (date_now - users_date).days
                if date_diff == 0:
                    same_day_counter += 1
                if same_day_counter >= 3:
                    same_day = True
                    break
        if same_day == True:
            pass
            # limit the number of checkouts per day
            #return redirect("pages:index")

        return super(OrderWizard, self).render_to_response(context, **response_kwargs)

    def done(self, form_list, **kwargs):
        ''' persist the order infos and handle the payment '''

        session_id = self.request.session.session_key
        order_products = get_order(session_id)

        # persist the checkout infos
        form_data = [form.cleaned_data for form in form_list]
        recapatcha = form_data[-1]
        if 'recapatcha' in recapatcha:
            secret_key = settings.RECAPTCHA_SECRET_KEY
            # captcha verification
            data = {
                'response': recapatcha.get('recapatcha'),
                'secret': secret_key
            }
            resp = requests.post(
                'https://www.google.com/recaptcha/api/siteverify', data=data)
            result_json = resp.json()

            if not result_json.get('success'):
                message_alert = {
                    'message': 'bots activity detected',
                    'sub_message': 'recapatcha verification failed',
                    'message_tag': 'warning',
                    'message_icon': 'czi-security-announcement'
                }
                self.request.session['message_alert'] = message_alert
                return redirect("pages:index")
        else:
            message_alert = {
                'message': 'bots activity detected',
                'sub_message': 'recapatcha verification failed',
                'message_tag': 'warning',
                'message_icon': 'czi-security-announcement'
            }
            self.request.session['message_alert'] = message_alert
            return redirect("pages:index")

        # fetch the shipping infos
        shipment_infos = Shipping(
            first_name=form_data[0].get('first_name'),
            last_name=form_data[0].get('last_name'),
            email=form_data[0].get('email'),
            telephone=form_data[0].get('telephone'),
            company=form_data[0].get('company'),
            country=form_data[0].get('country'),
            address=form_data[0].get('address'),
            street=form_data[0].get('street'),
            city=form_data[0].get('city'),
            region=form_data[0].get('region'),
            zip=form_data[0].get('zip'),
            fax=form_data[0].get('fax'),
            same_billing_address=form_data[0].get('same_billing_address')
        )

        # fetch the billing infos
        billing_infos = None
        if form_data[0].get('same_billing_address') == True:
            billing_infos = Billing(
                first_name_b=form_data[0].get('first_name'),
                last_name_b=form_data[0].get('last_name'),
                telephone_b=form_data[0].get('telephone'),
                company_b=form_data[0].get('company'),
                country_b=form_data[0].get('country'),
                address_b=form_data[0].get('address'),
                street_b=form_data[0].get('street'),
                city_b=form_data[0].get('city'),
                region_b=form_data[0].get('region'),
                zip_b=form_data[0].get('zip'),
                fax_b=form_data[0].get('fax')
            )
        else:
            billing_infos = Billing(
                first_name_b=form_data[1].get('first_name_b'),
                last_name_b=form_data[1].get('last_name_b'),
                telephone_b=form_data[1].get('telephone_b'),
                company_b=form_data[1].get('company_b'),
                country_b=form_data[1].get('country_b'),
                address_b=form_data[1].get('address_b'),
                street_b=form_data[1].get('street_b'),
                city_b=form_data[1].get('city_b'),
                region_b=form_data[1].get('region_b'),
                zip_b=form_data[1].get('zip_b'),
                fax_b=form_data[1].get('fax_b')
            )

        # the index of the shipment and payment relative to the billing choice
        i = 2
        if form_data[0].get('same_billing_address') == True:
            i = 1

        # fetch shipment method and the shipping price
        shipping_method = form_data[i].get('shipping_method')

        # fetch payment method
        payment_method = form_data[i+1].get('payment_method')

        # fetch customer infos
        customer_infos = Customer(
            first_name_c=form_data[0].get('first_name'),
            last_name_c=form_data[0].get('last_name'),
            phone_c=form_data[0].get('telephone'),
            email_c=form_data[0].get('email'),
            address_c=form_data[0].get('address'),
            street_c=form_data[0].get('street'),
            city_c=form_data[0].get('city'),
            region_c=form_data[0].get('region'),
            zip_c=form_data[0].get('zip'),
            fax_c=form_data[0].get('fax'),
            session_key_c=session_id
        )

        customer_infos.save()
        shipment_infos.save()
        billing_infos.save()

        # persist the order data
        checkout_infos = CheckoutModel.objects.create(
            customer=customer_infos,
            shiping_infos=shipment_infos,
            billing_infos=billing_infos,
            shipping_method=shipping_method,
            payment_method=payment_method,
            order=order_products,
            checkout_date=datetime.now(timezone.utc)
        )

        # empty the users cart
        order_products.ordered = True
        order_products.save()
        # mark the ordered products as ordered for the user
        for product_order in order_products.products.all():
            product_order.ordered = True
            product_order.save()

        # TO-DO handle payment

        # confirm the order to the user through E-mail after successful payment
        msg_html, email_address = get_email_infos(
            checkout_infos, False)
        confirm_with_email.delay(msg_html, email_address)

        # save the users email in mailchimp
        subscribe(customer_infos.email_c)

        return redirect("checkout:payment", checkout_infos.id)


class PaymentView(View):
    template_name = 'pages/checkout/checkout_complete.html'

    def get(self, request, *args, **kwargs):

        order_nr = self.kwargs['order_nr']
        context = {
            'order_number': order_nr
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        print('opst crap')
        return redirect("checkout:payment")


def get_order(session_id):
    try:
        order = Order.objects.get(session_key=session_id, ordered=False)
    except:
        order = None
    return order
