from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, DetailView, View
from stock.models import Product, CATEGORY_CHOICES
from django.core.paginator import Paginator
from .forms import SearchForm
from .models import Wishlist, Contact, ShippingInfo, About
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta, timezone


class IndexView(ListView):
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        new_products = Product.objects.active_products()[:6]
        selections = Product.objects.active_selections()[:8]

        new_clothing = Product.objects.active_clothing()[:6]
        new_cosmetics = Product.objects.active_cosmetics()[:6]
        print(new_cosmetics)
        # get the favorites items
        favorites = []
        message_alert = {}
        if request.session.session_key:
            session_id = request.session.session_key
            favorites_products = Wishlist.objects.filter(
                session_key=session_id).values('products').all()
            for favorite in favorites_products:
                product_id = favorite.get('products', None)
                if product_id is not None:
                    favorite_product = Product.objects.get(id=product_id)
                    favorites.append(favorite_product.slug)
            # check for alerts messages in the session
            if 'message_alert' in request.session: 
                message_alert = request.session['message_alert']
                request.session['message_alert'] = {}
            else:
                message_alert = {}
        
        context = {
            'new_products': new_clothing,
            'new_cosmetics': new_cosmetics,
            'selections': selections,
            'favorites': favorites,
            'message_alert': message_alert,
        }

        return render(request, self.template_name, context)


class ProductsView(View):
    template_name = 'pages/products.html'

    def get(self, request, *args, **kwargs):

        category = ''
        category_param = self.kwargs['category']

        # get the key of a url value parameter
        for k, v in dict(CATEGORY_CHOICES).items():
            if v == category_param:
                category = k
                break

        if len(category) != 0:
            products = Product.objects.active_categories(category)
            paginator = Paginator(products, 12)
            page_number = request.GET.get('page')
            paginator.get_page(page_number)
            page_obj = paginator.get_page(page_number)

            context = {
                'products': products,
                'category': category_param,
                'page_obj': page_obj
            }

        return render(request, self.template_name, context)


class SearchView(View):
    template_name = 'pages/search.html'

    def get(self, request, *args, **kwargs):
        search_query = self.kwargs['param']

        products = Product.objects.active_searched(search_query)
        paginator = Paginator(products, 12)
        page_number = request.GET.get('page')
        paginator.get_page(page_number)
        page_obj = paginator.get_page(page_number)

        context = {
            'products': products,
            'page_obj': page_obj
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = SearchForm(self.request.POST)
        search_query = ''
        if form.is_valid():
            search_query = form.cleaned_data.get('search_input')

        return HttpResponseRedirect(reverse('pages:search', kwargs={'param': search_query}))


class WishlistView(View):
    template_name = 'pages/wishlist.html'
    empty_wishlist = 'pages/subscribe.html'

    def get(self, request, *args, **kwargs):
        context = {}
        favorites = []
        if not request.session.session_key:
            return render(request, self.empty_wishlist, {})
        else:
            session_id = request.session.session_key
            users_wishlist = Wishlist.objects.filter(session_key=session_id)
            if users_wishlist.exists():
                wishlist = users_wishlist[0]
                favorites_count = wishlist.products.count()
                if favorites_count == 0:
                    return render(request, self.empty_wishlist, {})
                else:
                    favorites_products = Wishlist.objects.filter(
                        session_key=session_id).values('products').all()
                    for favorite in favorites_products:
                        product_id = favorite.get('products', None)
                        if product_id is not None:
                            favorite_product = Product.objects.get(
                                id=product_id)
                            favorites.append(favorite_product)
                            context['favorites'] = favorites
                return render(request, self.template_name, context)
        return render(request, self.template_name, context)



@require_http_methods(["POST"])
def addToFavorites(request):
    ''' process adding / removing a product from the favorites list '''

    if request.method == "POST":
        # create session key if there is none
        if not request.session.session_key:
            request.session.create()
            end_date = datetime.now(timezone.utc) + timedelta(days=30)
            request.session.set_expiry(end_date)
        session_id = request.session.session_key

        product_slug = request.POST.get('slug', None)
        if product_slug is None:
            return JsonResponse({'status': 'slug is not valid'})

        # get the product
        product_choice = Product.objects.get(slug=product_slug)

        # get the whishlist of the user
        users_wishlist = Wishlist.objects.filter(session_key=session_id)

        favorites_count = 0
        if users_wishlist.exists():
            wishlist = users_wishlist[0]
            # check if the product is in the wishlist
            if wishlist.products.filter(slug=product_slug).exists():
                p = wishlist.products.filter(slug=product_slug)[0]
                wishlist.products.remove(p)
            else:
                wishlist.products.add(product_choice)
            favorites_count = wishlist.products.count()
        else:
            whishlist = Wishlist.objects.create(
                session_key=session_id,
            )
            whishlist.products.add(product_choice)
            favorites_count = 1

    return JsonResponse({'status': 'order processed in favorites', 'counts': favorites_count})


@require_http_methods(["POST"])
def removeFromFavorites(request, slug):
    ''' remove a product with a slug as a parameter from the favorite list '''
    template_name = 'pages/wishlist.html'
    empty_wishlist = 'pages/subscribe.html'

    if request.method == "POST":
        if not request.session.session_key:
            return render(request, empty_wishlist, {})
        session_id = request.session.session_key
        product_slug = slug
        if product_slug is None:
            return HttpResponseRedirect(reverse('pages:wishlist'))
        # get the product
        product_choice = Product.objects.get(slug=product_slug)

        # get the whishlist of the user
        users_wishlist = Wishlist.objects.filter(session_key=session_id)
        favorites_count = 0
        if users_wishlist.exists():
            wishlist = users_wishlist[0]
            # check if the product is in the wishlist
            if wishlist.products.filter(slug=product_slug).exists():
                p = wishlist.products.filter(slug=product_slug)[0]
                wishlist.products.remove(p)
            else:
                return HttpResponseRedirect(reverse('pages:wishlist'))
            favorites_count = wishlist.products.count()
        else:
            return render(request, empty_wishlist, {})
    if favorites_count == 0:
        return render(request, empty_wishlist, {})
    else:
        return HttpResponseRedirect(reverse('pages:wishlist'))


@require_http_methods(["POST"])
def get_share_url(request):
    if request.method == 'POST':
        if not request.session.session_key:
            return JsonResponse({})
        session_id = request.session.session_key
        wishlist_cart = Wishlist.objects.filter(session_key=session_id)
        if wishlist_cart.exists():
            wishlist = wishlist_cart[0]
            wishlist_url = request.scheme + '://' + request.META['HTTP_HOST'] + '/wishlist/' + wishlist.url
            return JsonResponse({'url': wishlist_url})
    return JsonResponse({})

@require_http_methods(["GET"])
def show_wishlist( request, *args, **kwargs):
    template_name = 'pages/wishlist_extern.html'
    empty_wishlist = 'pages/empty_wishlist.html'
    search_query = kwargs['param']
    context = {}
    favorites = []
    wishlist_qs = Wishlist.objects.filter(url=search_query).values('products').all()
    if wishlist_qs.exists():
        for favorite in wishlist_qs:
            product_id = favorite.get('products', None)
            if product_id is not None:
                favorite_product = Product.objects.get(id=product_id)
                favorites.append(favorite_product)
        context['favorites'] = favorites
        return render(request, template_name, context)
    return render(request, empty_wishlist, context)
    
class ContactPage(ListView):
    model = Contact
    template_name = "pages/contact.html"

class AboutPage(ListView):
    model = About
    template_name = "pages/about.html"

class ShippingPage(ListView):
    model = ShippingInfo
    template_name = "pages/shipping_infos.html"