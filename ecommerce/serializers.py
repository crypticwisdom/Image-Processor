from django.db.models import Sum, Avg

from .models import ProductCategory, Product, ProductDetail, ProductImage, ProductReview, Promo, ProductType, \
    ProductWishlist
from rest_framework import serializers


# Hot New Arrivals Serializers #
class ProductDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        return [str(instance.image.url) for instance in ProductImage.objects.filter(product_detail=obj)]

    class Meta:
        model = ProductDetail
        exclude = []


class ProductSerializer(serializers.ModelSerializer):
    store = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    product_detail = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    def get_store(self, obj):
        return {"id": obj.store.id, "name": obj.store.name}

    def get_total_stock(self, obj):
        query = ProductDetail.objects.filter(product=obj)
        if query:
            return query.aggregate(Sum('stock')).get('stock__sum') or 0

    def get_brand(self, obj):
        if obj.productdetail.brand:
            return obj.productdetail.brand.name
        return None

    def get_average_rating(self, obj):
        rating = 0
        query_set = ProductReview.objects.filter(product=obj).aggregate(Avg('rating'))
        if query_set:
            rating = query_set['rating__avg']
        return rating

    def get_image(self, obj):
        image = None
        if obj.image:
            image = obj.image.image.url
        return image

    def get_product_detail(self, obj):
        serializer = ProductDetailSerializer(ProductDetail.objects.filter(product=obj).order_by('-stock').first())
        return serializer.data

    def get_category(self, obj):
        return obj.category.name

    class Meta:
        model = Product
        exclude = []
# END #


class ProductTypeSerializer(serializers.ModelSerializer):
    sub_category_id = serializers.IntegerField(source="category.id")

    class Meta:
        model = ProductType
        exclude = ["category"]


class CategoriesSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    sub_categories = serializers.SerializerMethodField()
    product_types = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                image = request.build_absolute_uri(obj.image.url)
                return image
            return obj.image.url

    def get_sub_categories(self, obj):
        cat = None
        if ProductCategory.objects.filter(parent=obj).exists():
            cat = [{"id": cat.id, "name": cat.name} for cat in ProductCategory.objects.filter(parent=obj)]
        return cat

    def get_product_types(self, obj):
        prod_type = None
        if ProductType.objects.filter(category=obj).exists():
            prod_type = ProductTypeSerializer(ProductType.objects.filter(category=obj), many=True).data
        return prod_type

    class Meta:
        model = ProductCategory
        exclude = []
        depth = 1


class MallDealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promo
        fields = ['product', ]
        depth = 1


class ProductWishlistSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    def get_product(self, obj):
        product = None
        if obj.product:
            product = ProductSerializer(obj.product).data
        return product

    class Meta:
        model = ProductWishlist
        exclude = []
