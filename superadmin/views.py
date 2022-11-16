from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser

from ecommerce.pagination import CustomPagination
from ecommerce.serializers import *

from account.serializers import *


class DashboardAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({})


# Product Start
class ProductListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    serializer_class = [ProductSerializer]
    queryset = Product.objects.all().order_by("-id")


class ProductRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = [ProductSerializer]
    queryset = Product.objects.all()
    lookup_field = "id"
# Product End


# Profile Start
class ProfileListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all().order_by("-id")
    pagination_class = CustomPagination


class ProfileDetailRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    lookup_field = "id"
# Profile End


# Brand Start
class BrandListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = BrandSerializer
    queryset = Brand.objects.all().order_by("-id")
    pagination_class = CustomPagination


class BrandDetailRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = BrandSerializer
    queryset = Brand.objects.all()
    lookup_field = "id"

# Brand End

# class ProductCate


