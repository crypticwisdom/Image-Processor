from rest_framework import serializers

from ecommerce.models import Cart
from merchant.models import Seller
from store.serializers import CartSerializer
from .models import Profile, Address
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()

    def get_phone_number(self, obj):
        phone_no = None
        if Profile.objects.filter(user=obj).exists():
            phone_no = Profile.objects.get(user=obj).phone_number
        return phone_no

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone_number']


class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = []


class ProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    addresses = serializers.SerializerMethodField()
    user = UserSerializer()
    is_merchant = serializers.SerializerMethodField()
    cart = serializers.SerializerMethodField()

    def get_cart(self, obj):
        request = self.context.get("request")
        if Cart.objects.filter(user=obj.user, status="open").exists():
            return CartSerializer(Cart.objects.filter(user=obj.user, status="open").last(), context={"request": request}).data
        return None

    def get_is_merchant(self, obj):
        if Seller.objects.filter(user=obj.user).exists():
            return True
        return False

    def get_profile_picture(self, obj):
        image = None
        if obj.profile_picture:
            image = obj.profile_picture.url
        return image

    def get_addresses(self, obj):
        address = None
        if Address.objects.filter(customer=obj).exists():
            address = CustomerAddressSerializer(Address.objects.filter(customer=obj), many=True).data
        return address

    class Meta:
        model = Profile
        fields = ['id', 'user', 'profile_picture', 'addresses', 'verified', 'has_wallet', 'is_merchant', 'cart']
