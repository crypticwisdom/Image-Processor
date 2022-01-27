from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from home.pagination import CustomPagination
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status
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

from store.serializers import (
    BrandSerializer,
    ProductCategorySerializer,
    StoreSerializer,
    ProductSerializer,
    ProductDetailSerializer,
    ProductImageSerializer,
    ProductReviewSerializer,
    ProductWishlistSerializer,
    ShipperSerializer,
    CartSerializer,
    CartProductSerializer,
    CartBillSerializer,

)


class BrandView(APIView):
    permission_classes = []

    def get(self, request):
        queryset = Brand.objects.all()
        serializer = BrandSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductCategoryView(APIView):
    permission_classes = []

    def get(self, request):
        queryset = ProductCategory.objects.all()
        serializer = ProductCategorySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StoreView(APIView):
    permission_classes = []

    def get(self, request):
        queryset = Store.objects.all()
        serializer = StoreSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductView(APIView, CustomPagination):
    permission_classes = []

    def get(self, request, slug=None):
        products = serializer = None
        if slug is None:
            products = Product.objects.all()  # queryset
            paginated_query = self.paginate_queryset(products, request)  # paginating query set
            serialized_data = ProductSerializer(paginated_query, many=True).data  # serialize the pagianted query set
            paginated_response = self.get_paginated_response(serialized_data)  # get paginated response
            return Response(paginated_response.data)
        elif slug is not None:
            product = get_object_or_404(Product, slug=slug)
            serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)


class ProductDetailView(APIView):
    permission_classes = []

    def get(self, request, slug=None):
        queryset = ProductDetail.objects.get(product__slug=slug)
        serializer = ProductDetailSerializer(queryset, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductImageView(APIView):
    permission_classes = []

    def get(self, request):
        queryset = ProductImage.objects.all()
        serializer = ProductImageSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductReviewView(APIView):
    permission_classes = []

    def get(self, request):
        queryset = ProductReview.objects.all()
        serializer = ProductReviewSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductWishlistView(APIView):
    permission_classes = []

    def get(self, request):
        queryset = ProductWishlist.objects.all()
        serializer = ProductWishlistSerializer(queryset, many=True)
        # print(serializer.is_valid, serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShipperView(APIView):
    permission_classes = []

    def get(self, request):
        queryset = Shipper.objects.all()
        serializer = ShipperSerializer(queryset, many=True)
        # print(serializer.is_valid, serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartView(APIView):
    permission_classes = []

    def get(self, request):
        queryset = Cart.objects.all()
        serializer = CartSerializer(queryset, many=True)
        # print(serializer.is_valid, serializer.data, 'nnhh')
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartProductView(APIView):
    permission_classes = []

    def get(self, request):
        queryset = CartProduct.objects.all()
        serializer = CartProductSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartBillView(generics.ListAPIView):
    queryset = CartBill.objects.all()
    serializer_class = CartBillSerializer
