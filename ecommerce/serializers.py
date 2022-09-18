from store.models import Product, ProductCategory, ProductDetail, ProductImage, ProductWishlist, ProductReview
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from store.serializers import ProductSerializer, ProductDetailSerializer, ProductReviewSerializer, \
    ProductImageSerializer


# Hot New Arrivals Serializers #
class HotNewProductDetailSerializer(ModelSerializer):
    image = SerializerMethodField()

    def get_image(self, obj):
        return [str(instance.image) for instance in ProductImage.objects.filter(product_detail=obj)]

    class Meta:
        model = ProductDetail
        fields = ['id', 'image', 'price', 'discount']


class HotNewProductArrivalSerializer(ModelSerializer):
    product_detail = SerializerMethodField()
    product_review = SerializerMethodField()

    def get_product_detail(self, obj):
        return HotNewProductDetailSerializer(ProductDetail.objects.filter(product=obj), many=True).data

    def get_product_review(self, obj):
        return [str(i.rating) for i in ProductReview.objects.filter(product=obj)]

    class Meta:
        model = Product
        fields = ['id', 'name', 'product_detail', 'product_review']
# END #
