from django.urls import path

from .views import IndexView, ProductsView, SearchView, WishlistView, addToFavorites, removeFromFavorites, get_share_url, show_wishlist, ContactPage, AboutPage, ShippingPage

app_name = 'pages'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('products/<str:category>', ProductsView.as_view(), name='products'),
    path('search/', SearchView.as_view(), name='search'),
    path('search/<str:param>', SearchView.as_view(), name='search'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/<str:param>', show_wishlist, name='show_wishlist'),
    path('add-to-favorites/', addToFavorites, name='add_to_favorites'),
    path('get-share-url/', get_share_url, name='get_share_url'),
    path('remove-from-favorites/<str:slug>', removeFromFavorites, name='remove_from_favorites'),
    path('contact/', ContactPage.as_view(), name='contact'),
    path('about/',AboutPage.as_view(), name='about'),
    path('shipping/', ShippingPage.as_view(), name='shipping'),
]
