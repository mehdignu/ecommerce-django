from django.contrib import admin
from .models import CheckoutModel, Shipping, Billing, Customer
from django.utils.html import mark_safe

class CheckoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer','telephone' ,'customer_order', 'shipping', 'sum','delivered', 'payment_method', 'shiping_infos', 'billing_infos')
    readonly_fields = ['shipping_method', 'payment_method', 'checkout_date', 'order', 'shiping_infos', 'billing_infos', 'customer']

    def customer_order(self, obj):
        return mark_safe(obj.products_details())

    def telephone(self, obj):
        return obj.customer_contact()
    
    def sum(self, obj):
        return obj.products_sum()

    def shipping(self, obj):
        return obj.shipping_details()

admin.site.register(CheckoutModel, CheckoutAdmin)
admin.site.register(Shipping)
admin.site.register(Billing)
admin.site.register(Customer)