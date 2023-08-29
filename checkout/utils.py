from .forms import SHIPPING_PRICES, SHIPPING_OPTION, PAYMENT_OPTION
from django.template.loader import render_to_string
from django.core.mail import send_mail
from celery import shared_task

def get_email_infos(checkout_infos, sent=False):
    ''' get the necessary email infos to be passed to celery '''
    
    shipping_price = dict(SHIPPING_PRICES)[checkout_infos.shipping_method]

    # get the order products infos
    products_infos = []
    for product_order in checkout_infos.order.products.all():
        description = ''
        price = product_order.product.price
        if product_order.product.discount_price:
            price = product_order.product.discount_price

            if product_order.size != None and product_order.size  != 'None':
                description = product_order.product.title + ', Size: ' + product_order.size + ', Color: ' + product_order.color
            else:
                description = product_order.product.title 
        products_infos.append({
            'amount': product_order.quantity,
            'product_nr': product_order.product.id,
            'description': description,
            'price': price,
            'product_sum': product_order.quantity * price
        })

    expenses_infos = {}
    expenses_infos.update({'shipping_price': shipping_price})
    expenses_infos.update(
        {'total_sum': checkout_infos.order.get_total_sum() + shipping_price})

    # get the billing address infos
    billing_address_infos = {}
    billing_address_infos.update({'billing_address': checkout_infos.billing_infos.address_b + ', ' + checkout_infos.billing_infos.street_b + ', ' + checkout_infos.billing_infos.city_b + ', ' + checkout_infos.billing_infos.region_b
                                  + ', ' + checkout_infos.billing_infos.zip_b +
                                  ', ' + checkout_infos.billing_infos.country_b
                                  })

    # get the shipping address
    shipping_address_infos = {}
    shipping_address_infos.update({'shipping_address': checkout_infos.shiping_infos.address + ', ' + checkout_infos.shiping_infos.street + ', ' + checkout_infos.shiping_infos.city + ', ' + checkout_infos.shiping_infos.region
                                   + ', ' + checkout_infos.shiping_infos.zip +
                                   ', ' + checkout_infos.shiping_infos.country
                                   })

    # get the payment and shipment method
    shipping_value = dict(SHIPPING_OPTION)[checkout_infos.shipping_method]
    payment_value = dict(PAYMENT_OPTION)[checkout_infos.payment_method]

    checkout_methods = {
        'shipment_method': shipping_value,
        'payment_method': payment_value
    }

    message_body = ''
    if sent == True:
        message_body = 'email/message_sent.html'
    else:
        message_body = 'email/message_body.html'

    msg_html = render_to_string(message_body, {'products_infos': products_infos, 'expenses_infos': expenses_infos, 'billing_address_infos': billing_address_infos,
                                                            'shipping_address_infos': shipping_address_infos, 'checkout_methods': checkout_methods, 'user_name': checkout_infos.shiping_infos.first_name, 'checkout_date': checkout_infos.checkout_date,
                                                            'checkout_nr': checkout_infos.id
                                                            })

    return msg_html, checkout_infos.shiping_infos.email


@shared_task
def confirm_with_email(msg_html, email_address):
    ''' confirm the user order with email '''

    send_mail(
        'Thank you for your order!',
        'Order Confirmation',
        'Womens Fashion <no-reply@wmn-fashion.com>',
        [email_address],
        html_message=msg_html,
        fail_silently=True
    )

    return None