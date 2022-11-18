from django.conf import settings
from django.db.models import Sum, Avg
from .models import ProductCategory, Product, ProductDetail, ProductImage, ProductReview, Promo, ProductType, \
    ProductWishlist, CartProduct, OrderProduct, Order, ReturnedProduct, ReturnProductImage, ReturnReason, Brand
from rest_framework import serializers


# Hot New Arrivals Serializers #
class ProductDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        return [str(instance.image.url) for instance in ProductImage.objects.filter(product_detail=obj)]

    class Meta:
        model = ProductDetail
        exclude = []


class SimilarProductSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()

    def get_price(self, obj):
        query = ProductDetail.objects.filter(product=obj).first()
        if query:
            return query.price
        return None

    def get_discount(self, obj):
        query = ProductDetail.objects.filter(product=obj).first()
        if query:
            return query.discount
        return None

    def get_average_rating(self, obj):
        rating = 0
        query_set = ProductReview.objects.filter(product=obj).aggregate(Avg('rating'))
        if query_set:
            rating = query_set['rating__avg']
        return rating

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                image = request.build_absolute_uri(obj.image.image.url)
                return image
            return obj.image.image.url
        return None

    class Meta:
        model = Product
        fields = ["id", "name", "is_featured", "average_rating", "image", "price", "discount"]


class ProductSerializer(serializers.ModelSerializer):
    store = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    product_detail = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    similar = serializers.SerializerMethodField()

    def get_similar(self, obj):
        product = Product.objects.filter(
            store__is_active=True, status='active', product_type=obj.product_type
        ).order_by('?').exclude(pk=obj.id).distinct()
        if self.context.get('seller'):
            product = product.filter(store__seller=self.context.get('seller'))
        return SimilarProductSerializer(product[:int(settings.SIMILAR_PRODUCT_LIMIT)], many=True,
                                        context={"request": self.context.get("request")}).data

    def get_store(self, obj):
        return {"id": obj.store.id, "name": obj.store.name}

    def get_total_stock(self, obj):
        query = ProductDetail.objects.filter(product=obj)
        if query:
            return query.aggregate(Sum('stock')).get('stock__sum') or 0

    def get_brand(self, obj):
        if obj.brand:
            return obj.brand.name
        return None

    def get_average_rating(self, obj):
        rating = 0
        query_set = ProductReview.objects.filter(product=obj).aggregate(Avg('rating'))
        if query_set:
            rating = query_set['rating__avg']
        return rating

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                image = request.build_absolute_uri(obj.image.image.url)
                return image
            return obj.image.image.url
        return None

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
    brand = serializers.SerializerMethodField()
    parent_category = serializers.SerializerMethodField()

    def get_parent_category(self, obj):
        data = None
        if obj.parent:
            data = {"id": obj.parent.id, "name": obj.parent.name}
        return data

    def get_brand(self, obj):
        if not obj.parent:
            brand = [{"id": brand.id, "name": brand.name} for brand in obj.brands.all()]
            return brand
        return None

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
        exclude = ["brands", "parent"]


class MallDealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promo
        fields = ['product', ]
        depth = 1


class CartProductSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    item_price = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_name(self, obj):
        if obj:
            return obj.product_detail.product.name
        return None

    def get_description(self, obj):
        if obj:
            return obj.product_detail.description
        return None

    def get_item_price(self, obj):
        if obj:
            return obj.product_detail.price * obj.quantity
        return None

    def get_image(self, obj):
        if self.context.get('request'):
            request = self.context.get('request')
            return request.build_absolute_uri(obj.product_detail.product.image.get_image_url())
        return obj.product_detail.product.image.get_image_url() or None


    class Meta:
        model = CartProduct
        fields = ["id", "name", "image", "description", "price", "quantity", "item_price", "discount", "product_detail"]


class ProductWishlistSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    def get_product(self, obj):
        product = None
        if obj.product:
            product = ProductSerializer(obj.product, context={"request": self.context.get("request")}).data
        return product


    class Meta:
        model = ProductWishlist
        exclude = []


class OrderProductSerializer(serializers.ModelSerializer):
    seller_id = serializers.IntegerField(source="product_detail.product.store.seller.id")
    store_name = serializers.CharField(source="product_detail.product.store.name")
    product_name = serializers.CharField(source="product_detail.product.name")

    class Meta:
        model = OrderProduct
        exclude = ["product_detail"]


class OrderSerializer(serializers.ModelSerializer):
    order_products = serializers.SerializerMethodField()
    no_of_products = serializers.SerializerMethodField()
    order_calculation = serializers.SerializerMethodField()

    def get_order_calculation(self, obj):
        data = dict()
        order_product_total = OrderProduct.objects.filter(order=obj).aggregate(Sum("total"))["total__sum"] or 0
        # This part is commented out, to be implemented when shipping fee is functioning on the shipper's module
        # shipping_fee_total = OrderProduct.objects.filter(order=obj).aggregate(Sum("total"))["total__sum"] or 0
        shipping_fee_total = 100
        data["product_total"] = order_product_total
        data["shipping_fee"] = shipping_fee_total
        data["total"] = order_product_total + shipping_fee_total
        return data

    def get_no_of_products(self, obj):
        prod = 0
        if OrderProduct.objects.filter(order=obj).exists():
            prod = OrderProduct.objects.filter(order=obj).count()
        return prod

    def get_order_products(self, obj):
        if OrderProduct.objects.filter(order=obj).exists():
            return OrderProductSerializer(OrderProduct.objects.filter(order=obj), many=True).data
        return None

    class Meta:
        model = Order
        exclude = ["customer"]
        depth = 1


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        exclude = []


class ReturnProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                image = request.build_absolute_uri(obj.image.url)
                return image
            return obj.image.url
        return None

    class Meta:
        model = ReturnProductImage
        exclude = ["id", "return_product", "image"]


class ReturnReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnReason
        fields = ['id', 'reason']


class ReturnedProductSerializer(serializers.ModelSerializer):
    return_images = serializers.SerializerMethodField()
    return_date = serializers.SerializerMethodField()
    reason = ReturnReasonSerializer()


    def get_return_date(self, obj):
        if obj:
            return obj.created_on
        return None

    def get_return_images(self, obj):
        if ReturnProductImage.objects.filter(return_product=obj).exists():
            return_product_image = ReturnProductImage.objects.filter(return_product=obj)
            context = self.context.get("request")
            return ReturnProductImageSerializer(return_product_image, many=True, context={"request": context}).data
        return None

    class Meta:
        model = ReturnedProduct
        fields = ['id', 'returned_by', 'return_images', 'product', 'reason', 'status', 'payment_status', 'comment',
                  'return_date', 'updated_by', 'updated_on']

