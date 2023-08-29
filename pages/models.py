from django.db import models
from stock.models import Product
from tinymce.models import HTMLField
import random
import string

class Wishlist(models.Model):
    products = models.ManyToManyField(Product)
    session_key = models.CharField(max_length=40)
    url = models.CharField(max_length=160)

    def __str__(self):
        return f"{self.session_key}"

    def save(self, *args, **kwargs):
        # calling super so that the instance will get created and self.id will be accessible.
        super(Wishlist, self).save()
        if len(self.url) == 0:
            allowed_chars = ''.join((string.ascii_letters, string.digits))
            url = ''.join(random.choice(allowed_chars) for _ in range(128))
            try:
                wishlist_obj = Wishlist.objects.get(url=url)
                url += "-" + str(self.id)
            except Wishlist.DoesNotExist:
                pass
            self.url = url
            self.save()

class Contact(models.Model):
    body = HTMLField()

class About(models.Model):
    body = HTMLField()

class ShippingInfo(models.Model):
    body = HTMLField()

