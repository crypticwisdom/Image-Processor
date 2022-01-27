from rest_framework.serializers import ModelSerializer
from merchant.models import Seller
from rest_framework import serializers
from store.models import (
    Brand,
    ProductCategory,
    Store,
    Product,
    ProductDetail,
    ProductImage,
    ProductReview,
    ProductWishlist,
    Shipper,
    Cart,
    CartProduct,
    CartBill,
)


class BrandSerializer(ModelSerializer):
    class Meta:
        model = Brand
        exclude = ()


class ProductCategorySerializer(ModelSerializer):
    brands = BrandSerializer(many=True)

    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'parent', 'brands', 'created_on', 'updated_on']


# Seller Serializer from merchant ( this serializer should be from Seyi's Serializer for this class )
class SellerSerializer(ModelSerializer):
    class Meta:
        model = Seller
        exclude = ()
        # print(serializer.is_valid, serializer.data, 'nnhh')


class StoreSerializer(ModelSerializer):
    seller = SellerSerializer(many=False)
    # categories = ProductCategorySerializer(many=True)

    class Meta:
        model = Store
        depth = 1
        fields = [
            'id',
            'seller',
            'name',
            'logo',
            'description',
            'categories',
            'is_active',
            'created_on',
            'updated_on']




class ProductSerializer(ModelSerializer):
    '''
        This serializer is used for serializing Product Model
        and this serializer is used for listing out all products and
        retrieve a particular product.
    '''

    store = StoreSerializer(many=False)

    class Meta:
        model = Product
        fields = [
            'id',
            'store',
            'name',
            'slug',
            'category',
            'sub_category',
            'tags',
            'status',
            'created_on',
            'updated_on'
        ]
        depth = 2


class ProductDetailSerializer(ModelSerializer):
    product = ProductSerializer(many=False)
    brand = BrandSerializer(many=False)

    class Meta:
        model = ProductDetail
        fields = [
            'id',
            'product',
            'brand',
            'description',
            'sku',
            'size',
            'color',
            'weight',
            'length',
            'width',
            'height',
            'stock',
            'price',
            'discount',
            'low_stock_threshold',
            'shipping_days',
            'out_of_stock_date',
            'created_on',
            'updated_on',
        ]


class ProductImageSerializer(ModelSerializer):
    product_detail = ProductDetailSerializer(many=False)

    class Meta:
        model = ProductImage
        fields = [
            'id',
            'product_detail',
            'image',
            'created_on',
            'updated_on',
        ]


class ProductReviewSerializer(ModelSerializer):
    product = ProductSerializer(many=False)

    class Meta:
        model = ProductReview
        fields = ['id', 'product']


class ProductWishlistSerializer(ModelSerializer):
    product = ProductSerializer(many=False)

    class Meta:
        model = ProductWishlist
        fields = ['id', 'user', 'product']


class ShipperSerializer(ModelSerializer):
    class Meta:
        model = Shipper
        exclude = ()


class CartSerializer(ModelSerializer):
    class Meta:
        model = Cart
        exclude = ()


class CartProductSerializer(ModelSerializer):
    cart = CartSerializer(many=False)
    product_detail = ProductDetailSerializer(many=False)

    class Meta:
        model = CartProduct
        fields = [
            'cart',
            'product_detail',
            'price',
            'quantity',
            'discount',
            'status',
            'delivery_fee',
            'created_on',
            'updated_on',
        ]


class CartBillSerializer(ModelSerializer):
    shipper = ShipperSerializer(many=False)

    class Meta:
        model = CartBill
        fields = [
            'cart',
            'shipper',
            'item_total',
            'discount',
            'delivery_fee',
            'management_fee',
            'total',
            'created_on',
            'updated_on',
        ]


