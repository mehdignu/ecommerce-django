from django.contrib import admin

from .models import Product, Color, Size

class StockAdmin(admin.ModelAdmin):
    list_display = ('id' ,'title', 'price', 'discount_price', 'selection')
    list_display_links = ('id', 'title')
    list_per_page = 20
    search_fields = ('title', 'description')
    readonly_fields = ['slug']


class SizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'size_label','product_color', 'product_name', 'quantity')
    list_display_links = ('id', 'size_label')
    search_fields = ('size_label', 'color__color_name', 'color__product__title')
    list_filter = ('size_label', 'color__color_name')


admin.site.register(Product, StockAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Color)
