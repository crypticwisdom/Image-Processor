from rest_framework import serializers
from .models import Profile, Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = []


class ProfileSerializer(serializers.ModelSerializer):
    addresses = serializers.SerializerMethodField()

    def get_address(self, obj):
        address = None
        if Address.objects.filter(customer=obj).exists():
            address = AddressSerializer(Address.objects.filter(customer=obj), many=True).data
        return address

    class Meta:
        model = Profile
        exclude = []

