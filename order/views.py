from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView
from order.models import Order, ProductOrder

class CartView(ListView):
    cart_name = 'pages/checkout/shop-cart.html'
    cart_empty= 'pages/checkout/empty-cart.html'

    def get(self, request, *args, **kwargs):

        context = {}
        if not request.session.session_key:
            return render(request, self.cart_empty, {})
        else:
            try:
                session_id = request.session.session_key
                order = Order.objects.order_by('-id').get(session_key=session_id, ordered=False)

                # when opening the cart clean the cart from out of stock products
                for p in order.products.all():
                    if p.order_out_of_stock(p.color):
                        Order.delete(p)

                # check if all the ordered products are out of the stock
                if Order.empty_order(session_id):
                    return render(request, self.cart_empty)

                message_alert = {}
                if 'message_alert' in request.session: 
                    message_alert = request.session['message_alert']
                    request.session['message_alert'] = {}

                context = {
                    'order_products': order,
                    'message_alert': message_alert
                }

                return render(request, self.cart_name, context)
            except Order.DoesNotExist:
                return render(request, self.cart_empty)


