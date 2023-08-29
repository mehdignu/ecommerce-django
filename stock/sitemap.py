from django.contrib.sitemaps import Sitemap
from .models import Product
from django.shortcuts import render, redirect, reverse

class ProductsSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Product.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()