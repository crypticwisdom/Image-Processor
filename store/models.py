from django.db import models
from django.contrib.auth.models import User
from merchant.models import Seller
from .choices import *
from merchant.models import Seller


class Brand(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='brand-images', null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product-images', null=False)
    brands = models.ManyToManyField(Brand, related_name='brands', blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Product Categories'

    def __str__(self):
        return self.name


class Store(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='seller')
    name = models.CharField(max_length=100, null=True, blank=True)
    logo = models.ImageField(upload_to='store-logo')
    description = models.TextField()
    categories = models.ManyToManyField(ProductCategory)
    is_active = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}: {self.seller} - {self.name}"


class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=500, editable=True, null=True, blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, blank=True, null=True, related_name='category')
    sub_category = models.ForeignKey(ProductCategory, blank=True, null=True, on_delete=models.CASCADE)
    tags = models.TextField(blank=True, null=True)
    status = models.CharField(choices=product_status_choices, max_length=10, default='inactive')

    # Recommended Product: should be updated to 'True' once the merchant makes' payment.
    is_featured = models.BooleanField(default=False)

    # View Count: number of times the product is viewed by a particular user. To be updated when a user views the prod.
    view_count = models.PositiveBigIntegerField(default=0)

    # Top Selling: The highest sold product. Field updates when this product has been successfully paid for.
    sale_count = models.IntegerField(default=0)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductDetail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(help_text='Describe the product')
    sku = models.CharField(max_length=100, blank=True, null=True)
    size = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=100, default='White')
    weight = models.FloatField(default=0)
    length = models.FloatField(default=0)
    width = models.FloatField(default=0)
    height = models.FloatField(default=0)
    stock = models.IntegerField(default=1)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=20)
    discount = models.DecimalField(default=0, decimal_places=2, max_digits=20)
    low_stock_threshold = models.IntegerField(default=5)
    shipping_days = models.IntegerField(default=3)
    out_of_stock_date = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id}: {self.product}'


class ProductImage(models.Model):
    product_detail = models.ForeignKey(ProductDetail, on_delete=models.CASCADE, related_name='product_detail')
    image = models.ImageField(upload_to='product-images')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id}:{self.product_detail}'


class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    headline = models.CharField(max_length=250)
    review = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {}".format(self.user, self.product)


class ProductWishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {}".format(self.user, self.product)

    class Meta:
        verbose_name_plural = "Product Wishlists"


class Shipper(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    slug = models.CharField(max_length=20, unique=True)
    vat_fee = models.DecimalField(max_digits=10, decimal_places=2, default=7.5)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    cart_uid = models.CharField(max_length=100, default="", null=True, blank=True)
    status = models.CharField(max_length=20, default='open', choices=cart_status_choices)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}: {self.cart_uid}-{self.user}-{self.status}"


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product_detail = models.ForeignKey(ProductDetail, on_delete=models.CASCADE)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=20)
    quantity = models.IntegerField(default=0)
    discount = models.DecimalField(default=0, decimal_places=2, max_digits=20)
    status = models.CharField(max_length=20, default='open', choices=cart_status_choices)
    delivery_fee = models.DecimalField(default=0, decimal_places=2, max_digits=50, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}: {} {}".format(self.id, self.cart, self.product_detail)


class CartBill(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    shipper = models.ForeignKey(Shipper, on_delete=models.SET_NULL, blank=True, null=True)
    item_total = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    discount = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    delivery_fee = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    management_fee = models.DecimalField(decimal_places=2, max_digits=10, default=0.0)
    total = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} {}".format(self.cart, self.total)


DEAL_DISCOUNT_TYPE_CHOICES = (
    ('fixed', 'Fixed amount'), ('percentage', 'Percentage')
)


class Deals(models.Model):
    title = models.CharField(max_length=100)
    price_promo = models.BooleanField(default=False, help_text="Enter price if this is selected")
    merchant_promo = models.BooleanField(default=False, help_text="Select merchant(s) if this is selected")
    category_promo = models.BooleanField(default=False, help_text="Select category(s) if this is selected")
    sub_category_promo = models.BooleanField(default=False, help_text="Select sub_category(s) if this is selected")
    product_promo = models.BooleanField(default=False, help_text="Select product(s) if this is selected")
    price = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True, default=0)
    discount_type = models.CharField(max_length=50, default='fixed', choices=DEAL_DISCOUNT_TYPE_CHOICES)
    discount = models.IntegerField(help_text='Discount value, 1 means 1% if discount type is percentage, 1000 '
                                             'means fixed discount of 1000 if discount type is fixed', null=True,
                                   blank=True, default=0)
    details = models.TextField(null=True, blank=True)
    merchant = models.ManyToManyField(Seller, blank=True)
    category = models.ManyToManyField(ProductCategory, blank=True)
    sub_category = models.ManyToManyField(ProductCategory, blank=True, related_name='sub_category')
    product = models.ManyToManyField(Product, blank=True)
    banner_image = models.ImageField(upload_to='promo banners', null=True, blank=True)
    status_choice = (('active', 'Active'), ('inactive', 'Inactive'))
    status = models.CharField(max_length=50, default='active', choices=status_choice)
    created_on = models.DateTimeField(auto_now_add=True, )
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(f"{self.title}")
