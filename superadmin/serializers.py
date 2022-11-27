from abc import ABC

from django.contrib.auth.models import User
from rest_framework import serializers

from ecommerce.models import Promo, ProductCategory
from store.models import Store
from superadmin.models import Role, AdminUser
from superadmin.exceptions import InvalidRequestException


class RoleSerializerOut(serializers.ModelSerializer):
    class Meta:
        model = Role
        exclude = []


class AdminUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.CharField(source="user.email")
    role = RoleSerializerOut()

    class Meta:
        model = AdminUser
        exclude = ["user"]


class CreateAdminUserSerializerIn(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    role = serializers.CharField(required=True)

    def create(self, validated_data):
        f_name = validated_data.get("first_name")
        l_name = validated_data.get("last_name")
        email = validated_data.get("email")
        password = validated_data.get("password")
        role_id = validated_data.get("role")

        if not Role.objects.filter(id=role_id).exists():
            raise InvalidRequestException({"detail": "Invalid role selected"})

        if User.objects.filter(email=email).exists():
            raise InvalidRequestException({"detail": "User with this email already exist"})

        role = Role.objects.get(id=role_id)

        # Create user
        user, _ = User.objects.get_or_create(username=email)
        user.first_name = f_name
        user.last_name = l_name
        user.email = email
        user.is_staff = True
        user.set_password(password)
        user.save()

        # Create AdminUser
        admin_user, created = AdminUser.objects.get_or_create(user=user)
        admin_user.role = role
        admin_user.save()

        data = AdminUserSerializer(admin_user).data
        return data


class BannerSerializer(serializers.ModelSerializer):
    merchant = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    sub_category = serializers.SerializerMethodField()
    product_type = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    merchant_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    sub_category_name = serializers.SerializerMethodField()

    def get_merchant_name(self, obj):
        if obj.merchant:
            return [merchant.user.get_full_name() for merchant in obj.merchant.all()]

    def get_category_name(self, obj):
        if obj.category:
            return [category.name for category in obj.category.all()]

    def get_sub_category_name(self, obj):
        if obj.sub_category:
            return [sub_cat.name for sub_cat in obj.sub_category.all()]

    def get_product(self, obj):
        if obj.product:
            return [{
                'id': product.id,
                'name': product.name,
                'category': product.category.name,
                'store_name': product.store.name,
            } for product in obj.product.all()]

    def get_merchant(self, obj):
        if obj.merchant:
            merchants = list()
            for merchant in obj.merchant.all():
                store_id = store_name = None
                if Store.objects.filter(seller=merchant).exists():
                    store = Store.objects.filter(seller=merchant).last()
                    store_id = store.id
                    store_name = store.name

                merchants.append({
                    "id": merchant.id,
                    "name": merchant.user.get_full_name(),
                    "store_id": store_id,
                    "store_name": store_name,
                })
            return merchants

    def get_category(self, obj):
        if obj.category:
            return [
                {
                    "id": category.id,
                    "name": category.name,
                    "sub_categories": [
                        {'id': cat.id, 'name': cat.name}
                        for cat in ProductCategory.objects.filter(parent=category)]
                }
                for category in obj.category.all()
            ]

    def get_sub_category(self, obj):
        if obj.sub_category:
            return [
                {
                    "id": sub_cat.id,
                    "name": sub_cat.name,
                }
                for sub_cat in obj.sub_category.all()
            ]

    def get_product_type(self, obj):
        if obj.product_type:
            return [
                {
                    "id": prod_type.id,
                    "name": prod_type.name,
                }
                for prod_type in obj.product_type.all()
            ]

    class Meta:
        model = Promo
        exclude = []






