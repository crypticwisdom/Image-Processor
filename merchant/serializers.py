from rest_framework import serializers
from .models import Seller, SellerVerification, SellerFile
from store.serializers import StoreSerializer
from store.models import Store


class SellerVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerVerification
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
        if SellerVerification.objects.filter(seller=obj):
            verified = SellerVerificationSerializer(SellerVerification.objects.filter(seller=obj).last()).data
        return verified

    def get_file(self, obj):
        file = None
        if SellerFile.objects.filter(seller=obj).exists():
            file = SellerFileSerializer(SellerFile.objects.filter(seller=obj), many=True).data
        return file

    def get_store(self, obj):
        if Store.objects.filter(seller=obj).exists():
            return StoreSerializer(Store.objects.get(seller=obj)).data
        return None

    class Meta:
        model = Seller
        exclude = []





