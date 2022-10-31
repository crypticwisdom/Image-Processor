from rest_framework.permissions import IsAuthenticated

from account.utils import validate_email
from ecommerce.models import ProductCategory
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
    permission_classes = []

    """
        Note from the meeting, if a buyer signs up to become a Merchant, when logged in he should be able to see a clickable 
        section that takes him to his Merchant profile and also his Buyer's profile.
        Any body visiting this end-point must be a user and signed in
    """

    def post(self, request):
        try:
            # ------------------------------------------------
            user = request.user
            print(user, user.is_authenticated)
            email = request.data.get('email', None)
            if email is not None:
                check = validate_email(email)
                if not check:
                    return Response({"detail": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST)

            if user is not None and request.user.is_authenticated:
                msg, success = create_seller(request, user, email)
                if success:
                    return Response({"detail": f"{msg}"}, status=status.HTTP_200_OK)
            print('pppppppppppppppppppppppppp')
            if request.user.is_authenticated is False:
                password = request.data.get('password', None)
                if not password:
                    return Response({"detail": "Password field is required"}, status=status.HTTP_400_BAD_REQUEST)

                password_confirm = request.data.get('password_confirm', None)
                if not password_confirm:
                    return Response({"detail": "Password confirm field is required"},
                                    status=status.HTTP_400_BAD_REQUEST)

                if password_confirm != password_confirm:
                    return Response({"detail": "Passwords does not match"}, status=status.HTTP_400_BAD_REQUEST)
                # I used email to fill the username field since, there would be a duplicate error if i user a value.
                user = User.objects.create_user(username=email, email=email, password=password)
                print(user, "----------")
                msg, success = create_seller(request, user, email)
                print(user, "----------", msg, success)

                if success:
                    return Response({"detail": f"{msg}"}, status=status.HTTP_200_OK)

            return Response({"detail": f"Something unexpected happened"}, status=status.HTTP_400_BAD_REQUEST)

        except (Exception,) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)
