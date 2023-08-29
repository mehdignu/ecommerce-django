from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', include('pages.urls', namespace='pages')),
    path('', include('stock.urls', namespace='stock')),
    path('', include('order.urls', namespace='order')),
    path('', include('marketing.urls', namespace='marketing')),
    path('tinymce/', include('tinymce.urls')),
    path('', include('checkout.urls', namespace='checkout')),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = views.handler404
handler500 = views.handler500