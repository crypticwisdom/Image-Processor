from rest_framework import serializers
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
        fields = ['id', 'user', 'profile_picture', 'addresses', 'verified']
