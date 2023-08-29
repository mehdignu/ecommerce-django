from django.db import models
from stock.models import Product, Color, Size
from django.utils.html import format_html

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)


class ProductOrder(models.Model):
    ''' a way of linking between the Order and the product.
        Storing product data that you want to order
    '''
    ordered = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.CharField(max_length=10, null=True)
    size = models.CharField(max_length=10, null=True)
    quantity = models.IntegerField(default=1)
    session_key = models.CharField(max_length=40)
    ordered = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.quantity} of {self.product.title}"
    
    def order_out_of_stock(self, color=None):
        ''' check if the order product is still in stock '''
        return self.product.out_of_stock(color)


class Order(models.Model):
    ''' the order is basically the shopping cart
        we add the items inside of it.
        Order information
    '''

    products = models.ManyToManyField(ProductOrder)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    session_key = models.CharField(max_length=40, null=True)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        order_details = '<ul>'
        for p in self.products.all():
            order_details += '<li>' + str(p.quantity) + ' of ' + p.product.title +'</li>'
        order_details += '</ul>'
        return format_html(order_details)

    def get_total_sum(self):
        sum = 0
        for product_order in self.products.all():
            if product_order.product.discount_price:
                sum += product_order.product.discount_price * product_order.quantity
            else:
                sum += product_order.product.price * product_order.quantity
        return sum

    def empty_order(session_id):
        ''' check if the cart is empty
            a cart can be fulled with products 
            that are out of stock but in this case it's empty
        '''
        empty_cart = True
        try:
            products_order = Order.objects.get(session_key=session_id, ordered=False)
            for product in products_order.products.all():
                if not product.order_out_of_stock():
                    empty_cart = False
                    break
        except Order.DoesNotExist:
            pass
        return empty_cart