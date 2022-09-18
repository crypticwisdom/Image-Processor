from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.views import APIView
from store.models import Product
from django.utils import timezone
from .serializers import MallProductArrivalSerializer, AllCategorySerializer
from store.models import ProductCategory
# Create your views here.


class MallLandPageView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            response, response_container = list(), dict()
            # Deals of the day

            # Hot New Arrivals
            start_date = timezone.datetime.today()
            end_date = timezone.timedelta(days=3)
            hot_new_arrivals = Product.objects.filter(created_on__date__gte=start_date - end_date)    # 3 days ago
            arrival_serialized = MallProductArrivalSerializer(hot_new_arrivals, many=True).data
            response_container["hot_new_arrivals"] = arrival_serialized

            # Top selling
            response_container["top_selling"] = ""

            # Top categories of the month
            response_container["top_selling"] = ""

            # Recommended Products
            recommended = MallProductArrivalSerializer(Product.objects.filter(is_featured=True), many=True).data
            response_container["recommended_products"] = recommended

            response.append(response_container)
            return Response({"detail": response}, status=HTTP_200_OK)
        except (Exception, ) as err:
            print(err)
            # LOG
            return Response({"detail": str(err)})


class AllCategoriesView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            serialized_data = AllCategorySerializer(ProductCategory.objects.all(), many=True).data
            return Response({"detail": serialized_data}, status=HTTP_200_OK)
        except (Exception, ) as err:
            return Response({"detail": str(err)}, status=HTTP_400_BAD_REQUEST)
