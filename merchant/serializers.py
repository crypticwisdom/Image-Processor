import json

from rest_framework import serializers
from ecommerce.models import ProductDetail, OrderProduct, Order
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
            verified = SellerVerificationSerializer(SellerDetail.objects.filter(seller=obj).last(), context=self.context).data
        return verified

    def get_file(self, obj):
        file = None
        if SellerFile.objects.filter(seller=obj).exists():
            file = SellerFileSerializer(SellerFile.objects.filter(seller=obj), many=True, context=self.context).data
        return file

    def get_store(self, obj):
        if Store.objects.filter(seller=obj).exists():
            request = self.context.get("request")
            store = [{
                "name": store.name,
                "logo": request.build_absolute_uri(store.logo.url),
                "description": store.name,
                # "categories": store.categories,
                "active": store.is_active
            } for store in Store.objects.filter(seller=obj)]
            return store
        return None

    class Meta:
        model = Seller
        exclude = []


class MerchantProductDetailsSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    sales = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.product.name

    def get_image(self, obj):
        if obj.product.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.product.image.image.url)
            return obj.product.image
        return None

    def get_sales(self, obj):
        return obj.product.sale_count

    def get_amount(self, obj):
        return self.get_sales(obj) * obj.price

    class Meta:
        model = ProductDetail
        fields = ['id', 'name', 'color', 'image', 'price', 'description', 'sales', 'amount']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class MerchantDashboardOrderProductSerializer(serializers.ModelSerializer):
    order_id = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    def get_order_id(self, obj):
        if obj:
            return OrderProduct.objects.get(id=obj.id).order.id
        return None

    def get_customer_name(self, obj):
        if obj:
            return "{} {}".format(
                OrderProduct.objects.get(id=obj.id).order.customer.user.last_name,
                OrderProduct.objects.get(id=obj.id).order.customer.user.first_name
            )
        return None

    def get_date(self, obj):
        """
            Dates are returned based on the status of the Ordered Prouct.
            Return Delivery Date when the Ordered product is pending.
        """
        if obj:
            if obj.status == "delivered":
                return obj.delivered_on
            elif obj.status == "cancelled":
                return obj.cancelled_on
            # elif obj.status == "pending":  Ashavin: we don't need pending
            #     return obj.delivery_date
            elif obj.status == "paid":
                return obj.payment_on
            elif obj.status == "returned":
                return obj.returned_on
            elif obj.status == "shipped":
                return obj.shipped_on
            elif obj.status == "refunded":
                return obj.refunded_on
            elif obj.status == "packed":
                return obj.packed_on
        return obj.created_on

    class Meta:
        model = OrderProduct
        fields = ['order_id', 'customer_name', 'tracking_id', 'payment_method', 'date', 'status', 'total']
