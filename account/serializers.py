from rest_framework import serializers
from .models import Profile, Address


class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ["customer"]


class ProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    addresses = serializers.SerializerMethodField()

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
        exclude = ["user"]

