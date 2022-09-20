from django.shortcuts import render
from django.views.generic import ListView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.views import APIView
from store.models import Product
from django.utils import timezone
from .serializers import MallProductSerializer, AllCategoriesSerializer, MallCategorySerializer
from store.models import ProductCategory
from ecommerce.pagination import CustomPagination
from rest_framework.generics import ListAPIView
# Create your views here.


class MallLandPageView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            response, response_container, start_date = list(), dict(), timezone.datetime.today()

            # (1) Deals of the day
            response_container["deals_of_the_day"] = None

            # (2) Hot New Arrivals in last 3 days
            start_date = timezone.datetime.today()
            end_date1 = timezone.timedelta(days=3)
            hot_new_arrivals = Product.objects.filter(created_on__date__gte=start_date - end_date1)    # 3 days ago
            arrival_serializer = MallProductSerializer(hot_new_arrivals, many=True).data
            response_container["hot_new_arrivals"] = arrival_serializer

            # (3) Top-selling
            end_date2 = timezone.timedelta(weeks=1)
            # sale count would be updated by the Admin.
            # here, we would fetch the updated results made by the admin.
            top_selling = Product.objects.filter(sale_count=0, created_on__date__gte=start_date - end_date2)
            top_selling_serializer = MallProductSerializer(top_selling, many=True).data
            response_container["top_selling"] = top_selling_serializer[:15]

            # (4) Top categories of the month
            end_date3 = timezone.timedelta(weeks=4)
            # sale-count would be updated by the Admin.
            # here, we would fetch the updated results made by the admin.
            top_selling = Product.objects.filter(sale_count=0, created_on__date__gte=start_date - end_date3)
            categories_serializer = MallCategorySerializer(top_selling, many=True).data
            response_container["top_monthly_categories"] = categories_serializer

            # (5) Recommended Products
            recommended = MallProductSerializer(Product.objects.filter(is_featured=True), many=True).data
            response_container["recommended_products"] = recommended[:5]

            response.append(response_container)
            return Response({"detail": response}, status=HTTP_200_OK)
        except (Exception, ) as err:
            print(err)
            # LOG
            return Response({"detail": str(err)}, status=HTTP_400_BAD_REQUEST)


class AllCategoriesView(APIView, CustomPagination):
    permission_classes = []

    def get(self, request):
        try:
            query_set = ProductCategory.objects.filter().order_by("-id")

            paginate_queryset = self.paginate_queryset(query_set, request)
            serialized_data = AllCategoriesSerializer(paginate_queryset, many=True).data
            data = self.get_paginated_response(serialized_data).data
            return Response({"detail": data}, status=HTTP_200_OK)

        except (Exception, ) as err:
            return Response({"detail": str(err)}, status=HTTP_400_BAD_REQUEST)


class TopSellingProductsView(APIView, CustomPagination):
    permission_classes = []

    def get(self, request):
        try:
            start_date = timezone.datetime.today()
            end_date2 = timezone.timedelta(weeks=1)

            queryset = Product.objects.filter(sale_count=0, created_on__date__gte=start_date - end_date2).order_by("-id")
            paginated_query = self.paginate_queryset(queryset, request)
            data = self.get_paginated_response(MallProductSerializer(paginated_query, many=True).data).data

            return Response({"detail": data}, status=HTTP_200_OK)
        except (Exception, ) as err:
            print(err)
            # LOG ERROR
            return Response({"detail": str(err)}, status=HTTP_400_BAD_REQUEST)


class RecommendedProductView(APIView, CustomPagination):
    permission_classes = []

    def get(self, request):
        try:
            query_set = Product.objects.filter(is_featured=True).order_by("-id")
            data = MallProductSerializer(query_set, many=True).data

            paginated_query = self.paginate_queryset(query_set, request)
            data = self.get_paginated_response(data=data).data
            return Response({"detail": data}, status=HTTP_200_OK)
        except (Exception, ) as err:
            print(err)
            # LOG ERROR
            return Response({"detail": str(err)}, status=HTTP_400_BAD_REQUEST)
