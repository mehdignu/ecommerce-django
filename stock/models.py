from django.db.models import Q
from django.db import models
from django.shortcuts import reverse
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.db.models import Count
from django.utils.text import slugify
from tinymce.models import HTMLField
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

CATEGORY_CHOICES = (
    ('P', 'Pantalon'),
    ('C', 'chemise'),
    ('J', 'jupe'),
    ('E', 'ensemble'),
    ('cosmetic', 'cosmetic')
)

COLORS = (
    ('B', 'Black'),
    ('W', 'White'),
    ('Y', 'Yellow'),
    ('G', 'Green'),
    ('R', 'Red'),
)

HASHED_COLORS = (
    ('B', {'name': 'Black', 'value': '#0F0102;'}),
    ('R', {'name': 'Red', 'value': '#EB0030;'}),
    ('W', {'name': 'White', 'value': '#ffffff;'})

)

SIZE_LABEL = (
    ('S', 'S'),
    ('M', 'M'),
    ('L', 'L'),
    ('XL', 'XL'),
)

class ServiceManager(models.Manager):
    
    def active_clothing(self):
        ''' filter products by the id '''
        products = []
        for p in Product.objects.all().order_by('-id'):
            qs = Color.objects.filter(product=p.id)
            if (qs.exists() and not p.out_of_stock() and p.category != 'cosmetic'): 
                products.append(p)
        return products

    def active_cosmetics(self):
        ''' filter products by the id '''
        products = []
        for p in Product.objects.all().order_by('-id'):
            if ( not p.out_of_stock() and p.category == 'cosmetic'): 
                products.append(p)
        return products

    def active_categories(self, category):
        ''' filter products by category ''' 
        products = []
        for p in Product.objects.all().filter(category=category).order_by('-id'):
            qs = Color.objects.filter(product=p.id)
            if ((qs.exists() and not p.out_of_stock()) or (p.category == 'cosmetic' and not p.out_of_stock())): 
                products.append(p)
        return products

    def active_products(self):
        ''' filter products by the id '''
        products = []
        for p in Product.objects.all().order_by('-id'):
            qs = Color.objects.filter(product=p.id)
            if ((qs.exists() and not p.out_of_stock()) or (p.category == 'cosmetic' and not p.out_of_stock())): 
                products.append(p)
        return products

    def active_suggestions(self, slug):
        ''' get products suggestions excluding the same product '''
        products = []
        for p in Product.objects.all().order_by('-id'):
            qs = Color.objects.filter(product=p.id)
            if (((qs.exists() and not p.out_of_stock()) or (p.category == 'cosmetic' and not p.out_of_stock())) and (p.slug != slug)): 
                products.append(p)
        return products

    def active_selections(self):
        ''' filter products by the selection field '''
        products = []
        for p in Product.objects.all().filter(selection=True).order_by('-id'):
            qs = Color.objects.filter(product=p.id)
            if ((qs.exists() and not p.out_of_stock()) or (p.category == 'cosmetic' and not p.out_of_stock())): 
                products.append(p)
        return products
    
    def active_searched(self, search_query):
        ''' filter products by a search query '''
        products = []
        for p in Product.objects.all().filter(Q(title__icontains=search_query) | Q(description__icontains=search_query) | Q(category__icontains=search_query)).order_by('-id'):
            qs = Color.objects.filter(product=p.id)
            if ((qs.exists() and not p.out_of_stock()) or (p.category == 'cosmetic' and not p.out_of_stock())): 
                products.append(p)
        return products

class Product(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=30)
    description = HTMLField()
    slug = models.SlugField(default='slug-holder')
    selection = models.BooleanField()
    objects = ServiceManager()

    # for other products example cosmetics
    quantity = models.IntegerField(default=1)
    photo_main = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_1 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_2 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_3 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # calling super so that the instance will get created and self.id will be accessible.
        super(Product, self).save()
        if self.slug == 'slug-holder':
            slug = slugify(self.title)
            try:
                product_obj = Product.objects.get(slug=slug)
                slug += "-" + str(self.id)
            except Product.DoesNotExist:
                pass
            self.slug = slug
            self.save()

    def get_absolute_url(self):
        return reverse('stock:product', kwargs={
            'slug': self.slug
        })

    def out_of_stock(self, color=None):
        ''' check if a product is out of stock '''
        if self.category == 'cosmetic':
            if self.quantity > 0:
                return False
            else:
                return True

        total_quantity = 0
        if color is None:
            for color in Color.objects.filter(product_id=self.id).values('id'):
                total_quantity += Size.objects.filter(
                    color_id=color.get('id'), quantity__gt=0).count()
        else:
            col = [COLORS[0] for COLORS in COLORS if COLORS[1] == color][0]
            for color in Color.objects.filter(product_id=self.id, color_name=col).values('id'):
                total_quantity += Size.objects.filter(
                color_id=color.get('id'), quantity__gt=0).count()

        if total_quantity > 0:
            return False
        else:
            return True

    def get_hashed_colors(self):
        ''' get the hashed colors to render them on the product description '''
        colors = []
        for color in Color.objects.filter(product_id=self.id).values('color_name', 'id'):
            if color.get('color_name') in dict(HASHED_COLORS) and Size.objects.filter(color_id=color.get('id')).count() > 0:
                color = dict(HASHED_COLORS)[color.get('color_name')]
                colors.append(color)
        return colors

    def get_main_photo(self):
        ''' get the main photo of the product '''
        soldout = self.out_of_stock()
        color = Product.get_default_color(self.id, soldout)
        photos, color_id = Product.get_photos(color, self.id)
        return photos['photo_main']

    def get_product_details_of_color(self, color, product_id, soldout=False):
        ''' get the product details from the selected color '''
        # get default color when the color parameter is empty
        if len(color) == 0:
            color = Product.get_default_color(product_id, soldout)
        # get the photos of the selected product
        photos, color_id = Product.get_photos(color, product_id)

        # get the the sizes with quantity
        sizes = {}
        if soldout:
            for s in Size.objects.filter(color_id=color_id).values('size_label', 'quantity'):
                sizes.update({s.get('size_label'): s.get('size_label')})
        else:
            for s in Size.objects.filter(color_id=color_id, quantity__gt=0).values('size_label', 'quantity'):
                sizes.update({s.get('size_label'): s.get('size_label')})
        
        # get the category value from the key
        category_value = dict(CATEGORY_CHOICES)[self.category]

        if len(sizes) == 0:
            res = {}
        else:
            res = {'color': color, 'sizes': sizes, 'photos': photos, 'category_value': category_value}
        return res

    def get_quantity(self, color=None, size=None):
        quantity = -1
        if color is None or size is None:
            return quantity
        else:
            photos, color_id = Product.get_photos(color, self.id)
            col = [COLORS[0] for COLORS in COLORS if COLORS[1] == color][0]
            # product_color = Color.objects.filter(product_id=self.id, color_name=col).values('id')
            quantity = Size.objects.get(color_id=color_id, size_label=size).quantity
        return quantity


    def get_default_color(product_id, soldout=False):
        ''' select a default color '''
        color = ''
        defined_colors = [COLORS[0] for COLORS in COLORS]
        for pc in Color.objects.filter(product_id=product_id).values('id', 'color_name'):
            if soldout:
                if pc.get('color_name') in dict(COLORS) and Size.objects.filter(color_id=pc.get('id')).count() > 0:
                    color = dict(COLORS)[pc.get('color_name')]
                    break
            else:
                if pc.get('color_name') in dict(COLORS) and Size.objects.filter(color_id=pc.get('id'), quantity__gt=0).count() > 0:
                    color = dict(COLORS)[pc.get('color_name')]
                    break
        return color

    def get_photos(color, product_id):
        ''' get the photos from a product id and color '''
        
        # get key of the color example 'R'
        c = [COLORS[0] for COLORS in COLORS if COLORS[1] == color][0]
        # fetch the photos
        photos_query = Color.objects.filter(product_id=product_id, color_name=c).values(
            'photo_main', 'photo_1', 'photo_2', 'photo_3', 'id')
        photos = [photos_query[0] for photo in photos_query][0]
        color_id = photos.get('id')
        del photos['id']
        return photos, color_id


class Color(models.Model):
    color_name = models.CharField(choices=COLORS, max_length=1)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    photo_main = models.ImageField(upload_to='photos/%Y/%m/%d/')
    photo_1 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_2 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_3 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        color = dict(COLORS)[self.color_name]
        return f"{color}: {self.product.title}"

class Size(models.Model):
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    size_label = models.CharField(choices=SIZE_LABEL, max_length=2)
    quantity = models.IntegerField(default=1)

    class Meta:
        ordering = ['-id']

    def product_name(self):
        return self.color.product.title

    def product_color(self):
        return self.color

    def __str__(self):
        return self.size_label
