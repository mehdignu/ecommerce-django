from django.shortcuts import get_object_or_404
from .models import Product
from order.models import Order, ProductOrder
from django.utils import timezone
from datetime import datetime, timedelta, timezone

def add_cosmetic_to_cart(request, slug, amount):
    ''' add a selected order from product details to cart '''
    # create session key if there is none
    if not request.session.session_key:
        request.session.create()
        end_date = datetime.now(timezone.utc) + timedelta(days=30)
        request.session.set_expiry(end_date)
    session_id = request.session.session_key

    product = get_object_or_404(Product, slug=slug)
    product_order, created = ProductOrder.objects.get_or_create(
        product=product,
        color=None,
        size=None,
        session_key=session_id,
        ordered=False
    )
    order_qs = Order.objects.filter(session_key=session_id, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the product is in the cart
        if order.products.filter(product__slug=product.slug).exists():
            # if product.quantity > product_order.quantity:
            product_order.quantity += int(amount)
            product_order.save()
            return True
            # else:
            #     return False
        else:
            product_order.quantity = int(amount)
            product_order.save()
            order.products.add(product_order)
            return True
    else:
        ordered_date = datetime.now(timezone.utc)
        order = Order.objects.create(
            session_key=session_id, ordered_date=ordered_date
        )
        product_order.quantity = int(amount)
        product_order.save()
        order.products.add(product_order)
        return True
    return False


def add_to_cart(request, color, size, slug, amount):
    ''' add a selected order from product details to cart '''
    # create session key if there is none
    if not request.session.session_key:
        request.session.create()
        end_date = datetime.now(timezone.utc) + timedelta(days=30)
        request.session.set_expiry(end_date)
    session_id = request.session.session_key

    product = get_object_or_404(Product, slug=slug)
    product_order, created = ProductOrder.objects.get_or_create(
        product=product,
        color=color,
        size=size,
        session_key=session_id,
        ordered=False
    )
    order_qs = Order.objects.filter(session_key=session_id, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the product is in the cart
        if order.products.filter(product__slug=product.slug, color=color, size=size).exists():
            # if product.get_quantity(color, size) > product_order.quantity:
            product_order.quantity += int(amount)
            product_order.save()
            return True
            # else:
            #     return False
        else:
            product_order.quantity = int(amount)
            product_order.save()
            order.products.add(product_order)
            return True
    else:
        ordered_date = datetime.now(timezone.utc)
        order = Order.objects.create(
            session_key=session_id, ordered_date=ordered_date
        )
        product_order.quantity = int(amount)
        product_order.save()
        order.products.add(product_order)
        return True
    return False

