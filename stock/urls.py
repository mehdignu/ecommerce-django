from django.urls import path
from .views import ProductDetailView, add_to_cart, remove_from_cart, increase_product, decrease_product
from .sitemap import ProductsSitemap 
from django.urls import include
from django.contrib.sitemaps.views import sitemap

app_name = 'stock'

sitemaps = {
    'static': ProductsSitemap
}

urlpatterns = [
    path('product/<str:slug>', ProductDetailView.as_view(), name='product'),
    path('product/<str:slug>/<str:color>', ProductDetailView.as_view(), name='product_color'),
    path('remove-from-cart/<str:slug>/<str:color>/<str:size>', remove_from_cart, name='remove_from_cart'),
    path('decrease-from-cart/<str:slug>/<str:color>/<str:size>', decrease_product, name='decrease_from_cart'),
    path('increase-from-cart/<str:slug>/<str:color>/<str:size>', increase_product, name='increase_from_cart'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps})

]