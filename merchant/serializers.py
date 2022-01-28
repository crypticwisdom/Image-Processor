from rest_framework import serializers
from .models import Seller, SellerVerification, SellerFile

class SellerSerializer(serializers.ModelSerializer):
    first_name = serializers.StringRelatedField(source='user.first_name')
    last_name = serializers.StringRelatedField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    phone_number = serializers.IntegerField()

    class Meta:
        model = Seller
        fields = ('id', 'first_name',  'last_name', 'email', 'phone_number', 'status')


class SellerVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerVerification
        fields = ('id_card', 'cac_number')


class SellerFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerFile
        fields = ('file', )