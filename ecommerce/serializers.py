from store.models import Product, ProductCategory, ProductDetail, ProductImage, ProductReview, Promo
from rest_framework.serializers import ModelSerializer, SerializerMethodField


# Hot New Arrivals Serializers #
class MallProductDetailSerializer(ModelSerializer):
    image = SerializerMethodField()

    def get_image(self, obj):
        return [str(instance.image.url) for instance in ProductImage.objects.filter(product_detail=obj)]

    class Meta:
        model = ProductDetail
        fields = ['id', 'image', 'price', 'discount']


class MallProductSerializer(ModelSerializer):
    product_detail = SerializerMethodField()
    product_review = SerializerMethodField()

    def get_product_detail(self, obj):
        return MallProductDetailSerializer(ProductDetail.objects.filter(product=obj), many=True).data

    def get_product_review(self, obj):
        return [str(i.rating) for i in ProductReview.objects.filter(product=obj)]

    class Meta:
        model = Product
        fields = ['id', 'name', 'product_detail', 'product_review', 'sale_count', 'is_featured']
# END #


class MallCategorySerializer(ModelSerializer):
    category_detail = SerializerMethodField()

    def get_category_detail(self, obj):
        category = Product.objects.get(id=obj.id).category
        return {"category_id": category.id, "category_name": category.name, "category_image": category.image.url}

    class Meta:
        model = Product
        fields = ['category_detail']


class AllCategoriesSerializer(ModelSerializer):
    class Meta:
        model = ProductCategory
        exclude = ["created_on", "updated_on", "brands"]
        depth = 1


class MallDealSerializer(ModelSerializer):

    class Meta:
        model = Promo
        fields = ['product', ]
        depth = 1
