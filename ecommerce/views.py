from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.views import APIView
from store.models import Product
from django.utils import timezone
from .serializers import HotNewProductArrivalSerializer
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
            arrival_serialized = HotNewProductArrivalSerializer(hot_new_arrivals, many=True).data
            response_container["hot_new_arrivals"] = arrival_serialized[:5]

            # top_selling
            response_container["top_selling"] = []
            # print(hot_new_arrivals)
            response.append(response_container)

            # Top categories of the month

            # Top selling

            # Recommended Products
            return Response({"detail": response}, status=HTTP_200_OK)
        except (Exception, ) as err:
            print(err)
            # LOG
            return Response({"detail": str(err)})
