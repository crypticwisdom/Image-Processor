import json

from rest_framework import serializers
from ecommerce.models import ProductDetail, OrderProduct, Order, ReturnedProduct, ReturnProductImage
from ecommerce.serializers import ReturnReasonSerializer, ReturnProductImageSerializer
from .models import Seller, SellerDetail, SellerFile, MerchantBanner
from store.models import Store


class SellerDetailSerializer(serializers.ModelSerializer):
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
    detail = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()
    store = serializers.SerializerMethodField()

    def get_detail(self, obj):
        data = None
        if SellerDetail.objects.filter(seller=obj):
            data = SellerDetailSerializer(SellerDetail.objects.filter(seller=obj).last(), context=self.context).data
        return data

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
                "description": store.description,
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
    # category = serializers.CharField(source="product_detail__product__category__name")
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


class ProductLowAndOutOffStockSerializer(serializers.ModelSerializer):

    product_name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_product_name(self, obj):
        if obj:
            return obj.product.name
        return None

    def get_image(self, obj):
        if obj.product.image and self.context.get("request"):
            request = self.context.get("request")
            return request.build_absolute_uri(obj.product.image.image.url)
        return obj.product.image.get_image_url()

    class Meta:
        model = ProductDetail
        fields = ['id', 'product_name', 'image', 'stock', 'price', 'discount']


class MerchantReturnedProductSerializer(serializers.ModelSerializer):
    returned_by = serializers.CharField(source="returned_by.first_name")    # Creating a custom field "Method 1"
    attachment_images = serializers.SerializerMethodField()     # Creating a custom field "Method 2 (More Advanced)"
    return_date = serializers.DateTimeField(source="created_on")
    product_name = serializers.CharField(source="product.product_detail.product.name")
    product_image = serializers.SerializerMethodField()
    updated_by = serializers.CharField(source="updated_by.first_name")
    reason = ReturnReasonSerializer()

    def get_attachment_images(self, obj):
        if ReturnProductImage.objects.filter(return_product=obj).exists():
            return_product_image = ReturnProductImage.objects.filter(return_product=obj)
            request = self.context.get("request")
            if request:
                return ReturnProductImageSerializer(return_product_image, many=True, context={"request": request}).data
        return None

    def get_product_image(self, obj):
        if obj.product.product_detail.product.image:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.product.product_detail.product.image.get_image_url())
        return obj.product.product_detail.product.image.get_image_url()

    class Meta:
        model = ReturnedProduct
        fields = ['id', 'returned_by', 'attachment_images', 'product_name', 'product_image', 'reason', 'status',
                  'payment_status', 'comment', 'return_date', 'updated_by', 'updated_on']


class MerchantBannerSerializerOut(serializers.ModelSerializer):
    class Meta:
        model = MerchantBanner
        exclude = []


class MerchantBannerSerializerIn(serializers.Serializer):
    auth_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    seller_id = serializers.IntegerField(required=False)
    image = serializers.ImageField()
    size = serializers.CharField()
    is_active = serializers.BooleanField(required=False)

    def create(self, validated_data):
        user = validated_data.get("auth_user")
        seller = validated_data.get("seller_id")
        image = validated_data.get("image")
        size = validated_data.get("size")
        is_active = validated_data.get("is_active")

        if user.is_staff and seller:
            seller = Seller.objects.get(id=seller)
            banner = MerchantBanner.objects.create(
                seller=seller, banner_image=image, banner_size=size, is_active=is_active
            )
        else:
            seller = Seller.objects.get(user=user)
            banner = MerchantBanner.objects.create(seller=seller, banner_image=image, banner_size=size)

        data = MerchantBannerSerializerOut(banner, context=self.context).data
        return data

    def update(self, instance, validated_data):
        user = validated_data.get("auth_user")
        size = validated_data.get("size")
        image = validated_data.get("image")

        if user.is_staff:
            if validated_data.get("is_active"):
                instance.is_active = validated_data.get("is_active")
        if image:
            instance.banner_image = image
        if size:
            instance.banner_size = size
        instance.save()

        data = MerchantBannerSerializerOut(instance, context=self.context).data
        return data



