from django.db.models import Sum
from rest_framework import serializers

from ecommerce.models import ProductImage, ProductReview, ProductWishlist, CartProduct, Brand, Product, \
    ProductDetail, Shipper, Cart
from merchant.serializers import SellerSerializer
from .models import *


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        exclude = []


class ProductCategorySerializer(serializers.ModelSerializer):
    brands = BrandSerializer(many=True, read_only=True, )
    total_products = serializers.SerializerMethodField()
    total_variants = serializers.SerializerMethodField()

    def get_total_products(self, obj):
        total = 0
        if Product.objects.filter(category=obj).exists():
            total = Product.objects.filter(category=obj).count()
        return total

    def get_total_variants(self, obj):
        variants = 0
        if ProductDetail.objects.filter(product__category=obj).exists():
            variants = ProductDetail.objects.filter(product__category=obj).count()
        return variants

    class Meta:
        model = ProductCategory
        exclude = []


class StoreSerializer(serializers.ModelSerializer):
    seller = SellerSerializer(many=False)
    # categories = ProductCategorySerializer(many=True)

    class Meta:
        model = Store
        exclude = []
        depth = 2


class ProductSerializer(serializers.ModelSerializer):
    """
        This serializer is used for serializing Product Model
        and this serializer is used for listing out all products and
        retrieve a particular product.
    """

    store = StoreSerializer(many=False)

    class Meta:
        model = Product
        fields = [
            'store',
            'name',
            'category',
            'sub_category',
            'tags',
            'status',
            'created_on',
            'updated_on'
        ]
        depth = 2


class ProductDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)
    brand = BrandSerializer(many=False)

    class Meta:
        model = ProductDetail
        fields = [
            'id',
            'product',
            'brand',
            'description',
            'sku',
            'size',
            'color',
            'weight',
            'length',
            'width',
            'height',
            'stock',
            'price',
            'discount',
            'low_stock_threshold',
            'shipping_days',
            'out_of_stock_date',
            'created_on',
            'updated_on',
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    product_detail = ProductDetailSerializer(many=False)

    class Meta:
        model = ProductImage
        fields = [
            'id',
            'product_detail',
            'image',
            'created_on',
            'updated_on',
        ]


class ProductReviewSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)

    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'rating']


class ShipperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipper
        exclude = ()


class CartProductSerializer(serializers.ModelSerializer):
    variant_id = serializers.IntegerField(source="product_detail.id")
    store_name = serializers.CharField(source="product_detail.product.store.name")
    product_name = serializers.CharField(source="product_detail.product.name")
    description = serializers.CharField(source="product_detail.product.description")
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        image = None
        request = self.context.get("request")
        if Product.objects.filter(productdetail=obj).exists():
            prod = Product.objects.filter(productdetail=obj).last()
            image = request.build_absolute_uri(prod.image.image.url)
        # if ProductImage.objects.filter(product_detail=obj.product_detail).exists():
        #     prod_image = ProductImage.objects.filter(product_detail=obj.product_detail).first()
        #     image = request.build_absolute_uri(prod_image.image.image.url)
        return image

    class Meta:
        model = CartProduct
        fields = ['id', 'variant_id', 'store_name', 'product_name', 'description', 'image', 'price', 'quantity', 'discount', 'created_on', 'updated_on']


class CartSerializer(serializers.ModelSerializer):
    cart_products = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    amount_summary = serializers.SerializerMethodField()

    def get_amount_summary(self, obj):
        return CartProduct.objects.filter(cart=obj).aggregate(Sum("price"))["price__sum"] or 0

    def get_total_items(self, obj):
        return CartProduct.objects.filter(cart=obj).count() or 0

    def get_cart_products(self, obj):
        request = self.context.get("request")
        if CartProduct.objects.filter(cart=obj).exists():
            return CartProductSerializer(CartProduct.objects.filter(cart=obj), context={"request": request}, many=True).data
        return None

    class Meta:
        model = Cart
        exclude = ["user"]


