from django import template
from order.models import Order
from stock.models import Product, Color, CATEGORY_CHOICES
from pages.forms import SearchForm, MobileSearchForm
from pages.models import Wishlist
from marketing.forms import EmailSubscribeForm

register = template.Library()


@register.inclusion_tag('partials/_subscribe.html')
def show_subscription():
    return {'form_footer': EmailSubscribeForm()}


@register.filter
def cart_item_count(request):
    if not request.session.session_key:
        return 0
    else:
        session_id = request.session.session_key
        if Order.empty_order(session_id):
            return 0
        qs = Order.objects.filter(session_key=session_id, ordered=False)
        if qs.exists():
            c = 0
            for x in qs[0].products.all():
                c += x.quantity
            return c
        else:
            return 0


@register.filter
def cart_item_photos(product_id, color=None):
    if color is None:
        product = Product.objects.filter(id=product_id).values(
            'photo_main', 'photo_1', 'photo_2', 'photo_3', 'id')
        return product[0].get('photo_main')
    photos, color_id = Product.get_photos(color, product_id)
    return photos.get('photo_main')


@register.filter
def order_products(session_id):
    return 'session_id'


@register.filter
def get_categories(context='whatever'):
    categories = {}
    for k, v in CATEGORY_CHOICES:
        qs = Product.objects.filter(category=k)
        if qs.exists():
            categories[v] = k
    return categories


@register.filter
def get_category_from_key(key=''):
    if len(key) == 0:
        return None
    return dict(CATEGORY_CHOICES)[key]


@register.filter
def get_search_form(ph=True):
    return SearchForm()


@register.filter
def get_mobile_search_form(ph=True):
    return MobileSearchForm()


@register.filter
def split(value, key):
    return str(value).split(key)


@register.filter
def count_favorites(request):
    favorites_count = 0
    if not request.session.session_key:
        return favorites_count
    else:
        session_id = request.session.session_key
        users_wishlist = Wishlist.objects.filter(session_key=session_id)
        if users_wishlist.exists():
            wishlist = users_wishlist[0]
            favorites_count = wishlist.products.count()
    return favorites_count


@register.filter
def multiply_counter(counter):
    return counter*100

@register.filter
def multiply_counter_second(counter):
    return counter*1000

@register.filter
def isFavorite(request, slug):
    favorite = False
    if not request.session.session_key:
        return favorite
    else:
        session_id = request.session.session_key
        users_wishlist = Wishlist.objects.filter(
            session_key=session_id).values('products').all()
        for wish_product in users_wishlist:
            product_id = wish_product.get('products', None)
            if product_id is not None:
                favorite_product = Product.objects.get(
                    id=product_id)
                if slug == favorite_product.slug:
                    favorite = True
                    break
    return favorite
