from django.contrib import admin

from .models import Wishlist, Contact, ShippingInfo, About

admin.site.register(Wishlist)
admin.site.register(Contact)
admin.site.register(ShippingInfo)
admin.site.register(About)
