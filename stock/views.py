from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Product
from order.models import Order, ProductOrder
from django.utils import timezone
from datetime import datetime, timedelta, timezone
from .forms import ProductOrderForm, ProductSubscription, CosmeticOrderForm
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .utils import add_to_cart, add_cosmetic_to_cart

class ProductDetailView(DetailView):
    template_name = 'pages/product/product.html'
    soldout_template = 'pages/product/soldout.html'

    def get(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        product = Product.objects.get(slug=slug)
        soldout = False
        new_products = Product.objects.active_suggestions(slug)[:12]
        suggestions_style_with = new_products[::2]
        suggestions_may_like = new_products[1::2]

        if product.category == 'cosmetic':
            soldout = product.out_of_stock()
            photos_query = Product.objects.filter(id=product.id).values(
                'photo_main', 'photo_1', 'photo_2', 'photo_3', 'id')
            photos = [photos_query[0] for photo in photos_query][0]
            details = {'photos': photos, 'category_value': product.category, 'color': None}
            form = CosmeticOrderForm(request.POST or None)
        else:

            # get chosen color
            if 'color' in self.kwargs:
                color = self.kwargs['color']
                soldout = product.out_of_stock(color)
                details = product.get_product_details_of_color(
                    color, product.id, soldout)
            else:
                soldout = product.out_of_stock()
                # default product details with a default color if no color is chosen
                details = product.get_product_details_of_color(
                    '', product.id, soldout)

            if not soldout:
                form_initial = {
                    'sizes': details.get('sizes'),
                    'color': details.get('color')
                }
                form = ProductOrderForm(request.POST or None,
                                        initial=form_initial)
            else:
                form = ProductSubscription()

        if 'message_alert' in request.session: 
            message_alert = request.session['message_alert']
            request.session['message_alert'] = {}
        else:
            message_alert = {}

        context = {
            'object': product,
            'details': details,
            'form': form,
            'soldout': soldout,
            'message_alert': message_alert,
            'suggestions_style_with': suggestions_style_with,
            'suggestions_may_like': suggestions_may_like
        }

        return render(request, self.template_name, context)

    def post(self, request, slug, color=None, *args, **kwargs):
        slug = self.kwargs['slug']
        product_ordered = Product.objects.filter(slug=slug).values(
            'category', 'id')

        product_category = product_ordered[0].get('category')

        if product_category == 'cosmetic':

            # add a cosmetic product
             # form
            form = CosmeticOrderForm(self.request.POST or None)
            if form.is_valid():
                amount = form.cleaned_data.get('amount')
                product_added = add_cosmetic_to_cart(self.request, slug, amount)

            message_alert = {}
            if product_added == True:
                message_alert = {
                    'message': 'Success!',
                    'sub_message': 'Product added successfully to your cart!',
                    'message_tag': 'success',
                    'message_icon': 'czi-check-circle'
                }
            else:
                message_alert = {
                    'message': 'Maximum Quantity is reached',
                    'sub_message': 'You have reached the maximum quantity allowed',
                    'message_tag': 'warning',
                    'message_icon': 'czi-security-announcement'
                }
            request.session['message_alert'] = message_alert
            return redirect("stock:product", slug=slug)
        else:
            # add a clothing product
            # form
            form = ProductOrderForm(self.request.POST or None)
            if form.is_valid():
                color = form.cleaned_data.get('color')
                size = form.cleaned_data.get('size')
                amount = form.cleaned_data.get('amount')
                product_added = add_to_cart(self.request, color, size, slug, amount)

            message_alert = {}
            if product_added == True:
                message_alert = {
                    'message': 'Success!',
                    'sub_message': 'Product added successfully to your cart!',
                    'message_tag': 'success',
                    'message_icon': 'czi-check-circle'
                }
            else:
                message_alert = {
                    'message': 'Maximum Quantity is reached',
                    'sub_message': 'You have reached the maximum quantity allowed',
                    'message_tag': 'warning',
                    'message_icon': 'czi-security-announcement'
                }
            request.session['message_alert'] = message_alert
            return redirect("stock:product_color", slug=slug, color=color)
        return redirect("stock:product", slug=slug)


@require_http_methods(["POST"])
def remove_from_cart(request, slug, color=None, size=None):
    ''' remove a selected order from product details to cart '''
    if color == 'None':
        color = None
    if size == 'None':
        size = None

    # if the user have no session key, no cart is found
    if not request.session.session_key:
        return redirect('order:cart')
    session_id = request.session.session_key
    if request.method == 'POST':
        order_qs = Order.objects.filter(session_key=session_id, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the product is in the cart
            product_qs = order.products.filter(
                product__slug=slug, color=color, size=size)
            if product_qs.exists():
                # remove the product from the users order
                product = product_qs[0]
                # order.products.remove(product)
                Order.delete(product)
                if order.products.count() == 0:
                    order_qs.delete()
    return redirect('order:cart')


@require_http_methods(["POST"])
def increase_product(request, slug, color, size):
    ''' increase the quantity of the product in the cart '''
    # if the user have no session key, no cart is found
    if not request.session.session_key:
        return redirect('order:cart')
    session_id = request.session.session_key
    if color == 'None':
        color = None
    if size == 'None':
        size = None

    if request.method == 'POST':
        product = get_object_or_404(Product, slug=slug)
        product_order = get_object_or_404(ProductOrder,
                                          product=product,
                                          color=color,
                                          size=size,
                                          session_key=session_id,
                                          ordered=False)

        order_qs = Order.objects.filter(session_key=session_id, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the product is in the cart
            if order.products.filter(product__slug=product.slug, color=color, size=size).exists():
                # limit the cart amount with what the stock have
                # if product.get_quantity(color, size) > product_order.quantity:
                product_order.quantity += 1
                product_order.save()
                # else:
                #     message_alert = {
                #         'message': 'Maximum Quantity is reached',
                #         'sub_message': 'You have reached the maximum quantity allowed',
                #         'message_tag': 'warning',
                #         'message_icon': 'czi-security-announcement'
                #     }
                #     request.session['message_alert'] = message_alert
                return redirect('order:cart')
        else:     
            return redirect('order:cart')


@require_http_methods(["POST"])
def decrease_product(request, slug, color, size):
    ''' decrease the quantity of the product from the cart '''
    # if the user have no session key, no cart is found
    if not request.session.session_key:
        return redirect('order:cart')
    session_id = request.session.session_key

    if color == 'None':
        color = None
    if size == 'None':
        size = None

    if request.method == 'POST':
        product = get_object_or_404(Product, slug=slug)
        product_order = get_object_or_404(ProductOrder,
                                          product=product,
                                          color=color,
                                          size=size,
                                          session_key=session_id,
                                          ordered=False)

        order_qs = Order.objects.filter(session_key=session_id, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the product is in the cart
            if order.products.filter(product__slug=product.slug, color=color, size=size).exists():
                if product_order.quantity > 1:
                    product_order.quantity -= 1
                    product_order.save()
                return redirect('order:cart')
        else:     
            return redirect('order:cart')
