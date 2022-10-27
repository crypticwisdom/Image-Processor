from rest_framework.permissions import IsAuthenticated

from ecommerce.serializers import ProductSerializer
from .serializers import SellerSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from home.pagination import CustomPagination

from .utils import *


class MerchantView(APIView, CustomPagination):
    permission_classes = []

    def get(self, request, seller_id=None):

        try:
            if id:
                item = Seller.objects.get(id=seller_id)
                serializer = SellerSerializer(item)
            else:
                item = Seller.objects.all()
                item = self.paginate_queryset(item, request)
                serializer = SellerSerializer(item, many=True).data
                serializer = self.get_paginated_response(serializer)

            return Response(serializer.data)
        except Exception as ex:
            return Response({"detail": "Error getting object", "message": str(ex)},
                            status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        if request.user.is_anonymous:
            return Response({"status": False, "detail": "You must be logged in to perform this operation"},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            seller, created = Seller.objects.get_or_create(user=request.user)
            success = create_update_seller(seller, request)
            if success is True:
                # CREATE A THREAD TO SEND NOTIFICATION TO MERCHANT HERE

                serializer = SellerSerializer(seller).data
                return Response({"success": True, "detail": serializer})
        except Exception as ex:
            return Response({"success": False, "detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        if request.user.is_anonymous:
            return Response({"status": False,
                             "detail": "You must be logged in to perform this option"},
                            status=status.HTTP_400_BAD_REQUEST)

        seller = Seller.objects.get(user=request.user)
        if not seller:
            return Response({"success": False, "detail": "Invalid account selected"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            success = create_update_seller(seller, request)
            if success is True:
                serializer = SellerSerializer(seller).data
                return Response({"success": True, "detail": serializer})
        except Exception as ex:
            return Response({"success": False, "detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)


class MerchantLoginView(APIView):
    permission_classes = []

    def post(self, request):
        ...


class BecomeAMerchantView(APIView):
    permission_classes = [IsAuthenticated]

    """
        Note from the meeting, if a buyer signs up to become a Merchant, when logged in he should be able to see a clickable 
        section that takes him to his Merchant profile and also his Buyer's profile.
    """

    def post(self, request):
        try:
            # first_name, last_name = request.data.get("first_name", None), request.data.get("last_name", None)
            # phone_number, email = request.data.get("phone_number", None), request.data.get('email', None)
            # business_name =
            # product_category =
            # business_address =
            # business_state =
            # business_city =
            # business_drop_off_address =
            # business

            return Response({"detail": ""}, status=status.HTTP_200_OK)
        except (Exception, ) as err:
            return Response({"detail": ""}, status=status.HTTP_400_BAD_REQUEST)


class ProductAPIView(APIView):

    def post(self, request):
        try:
            if not Seller.objects.filter(user=request.user).exists():
                return Response({"detail": "Only merchant account can add product"}, status=status.HTTP_400_BAD_REQUEST)
            seller = Seller.objects.get(user=request.user)

            success, detail, product = create_product(request, seller)
            if success is False:
                return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": detail, "product": ProductSerializer(product).data})
        except Exception as err:
            return Response({"detail": "An error has occurred", "error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            store = Store.objects.get(seller__user=request.user)
            product = Product.objects.get(id=pk, store=store)
            query = update_product(request, product)
            return Response({"detail": "Product updated successfully", "product": ProductSerializer(query).data})
        except Exception as ess:
            return Response({"detail": "An error has occurred", "error": str(ess)}, status=status.HTTP_400_BAD_REQUEST)




