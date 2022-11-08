from rest_framework import serializers

from ecommerce.models import ProductDetail
from .models import Seller, SellerDetail, SellerFile
from store.models import Store


class SellerVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerDetail
        exclude = []


class SellerFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerFile
        fields = ['file']


class SellerSerializer(serializers.ModelSerializer):
    first_name = serializers.StringRelatedField(source='user.first_name')
    last_name = serializers.StringRelatedField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    phone_number = serializers.IntegerField()
    verification = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()
    store = serializers.SerializerMethodField()

    def get_verification(self, obj):
        verified = None
        if SellerDetail.objects.filter(seller=obj):
            verified = SellerVerificationSerializer(SellerDetail.objects.filter(seller=obj).last()).data
        return verified

    def get_file(self, obj):
        file = None
        if SellerFile.objects.filter(seller=obj).exists():
            file = SellerFileSerializer(SellerFile.objects.filter(seller=obj), many=True).data
        return file

    def get_store(self, obj):
        from store.serializers import StoreSerializer
        if Store.objects.filter(seller=obj).exists():
            return StoreSerializer(Store.objects.get(seller=obj)).data
        return None

    class Meta:
        model = Seller
        exclude = []


class MerchantProductDetailsSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    sales = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.product.name

    def get_image(self, obj):
        return obj.product.image.get_image_url()

    def get_sales(self, obj):
        return obj.product.sale_count

    def get_amount(self, obj):
        return self.get_sales(obj) * obj.price

    class Meta:
        model = ProductDetail
        fields = ['id', 'name', 'color', 'image', 'price', 'description', 'sales', 'amount']
