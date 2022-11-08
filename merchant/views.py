from rest_framework.permissions import IsAuthenticated

from account.models import Profile
from account.utils import validate_email
from .serializers import SellerSerializer, MerchantProductDetailsSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from home.pagination import CustomPagination
from .utils import *
from .permissions import IsMerchant
from ecommerce.models import ProductDetail, Product, ProductCategory
from ecommerce.serializers import ProductDetailSerializer
# Merchant is Seller


class MerchantView(APIView, CustomPagination):
    permission_classes = []

    def get(self, request, seller_id=None):

        try:
            if id:
                item = Seller.objects.get(id=seller_id)
                serializer = SellerSerializer(item)
            else:
                query_set = Seller.objects.all()
                paginated_query_set = self.paginate_queryset(query_set, request)
                serializer = SellerSerializer(paginated_query_set, many=True).data
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
        Authenticated users are allowed to see call this endpoint.
    """

    def post(self, request):
        try:
            # ------------------------------------------------
            user = request.user
            email = request.data.get('email', None)
            if email is not None:
                check = validate_email(email)
                if not check:
                    return Response({"detail": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST)

            phone_number = request.data.get('phone_number', None)
            if phone_number is not None and str(phone_number[-10:]).isnumeric():
                phone_number = f"{+234} {phone_number[-10:]}"
            else:
                return "Phone Number is required", False

            # Create Merchant for Authenticated User
            if user is not None and request.user.is_authenticated:
                if Seller.objects.filter(user=user).exists():
                    return Response({"detail": "You already have a merchant account"},
                                    status=status.HTTP_400_BAD_REQUEST)

                msg, success = create_seller(request, user, email, phone_number)
                if success:
                    return Response({"detail": f"{msg}"}, status=status.HTTP_200_OK)

            # Create Merchant for Un-Authenticated User
            # if request.user.is_authenticated is False:
            #     password = request.data.get('password', None)
            #     if not password:
            #         return Response({"detail": "Password field is required"}, status=status.HTTP_400_BAD_REQUEST)
            #
            #     password_confirm = request.data.get('password_confirm', None)
            #     if not password_confirm:
            #         return Response({"detail": "Password confirm field is required"},
            #                         status=status.HTTP_400_BAD_REQUEST)
            #
            #     if password_confirm != password_confirm:
            #         return Response({"detail": "Passwords does not match"}, status=status.HTTP_400_BAD_REQUEST)
            #
            #     # Check: If user details for un-authenticated user is found in the database the throw an error.
            #     check_for_user_existence = User.objects.filter(email=email)
            #     if check_for_user_existence.exists():
            #         return Response({"detail": f"This user detail already exist, please login to Register as a Merchant"}, status=status.HTTP_400_BAD_REQUEST)
            #
            #     # I used email to fill the username field since, there would be a duplicate error if i user a value.
            #     user = User.objects.create_user(username=email, email=email, password=password)
            #
            #     # Check: to see if this user instance has a profile instance else, create a profile
            #     if not Profile.objects.filter(user=user).exists():
            #         profile = Profile.objects.create(user=user, phone_number=phone_number)
            #
            #     msg, success = create_seller(request, user, email, phone_number)
            #
            #     if msg == "improper merchant creation" and success is True:
            #         return Response(
            #             {"detail": f"User created successfully but, an error happened during Merchant Registration, "
            #                        f"kindly login to register"}, status=status.HTTP_201_CREATED)
            #
            #     elif success is True:
            #         return Response({"detail": f"{msg}"}, status=status.HTTP_200_OK)

            return Response({"detail": f"Something unexpected happened"}, status=status.HTTP_400_BAD_REQUEST)
        except (Exception,) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)


class MerchantDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsMerchant]

    def get(self, request):
        try:
            print(request.user.is_authenticated, request.user)
            seller = Seller.objects.filter(user=request.user)
            print(seller)
            product_detail = ProductDetail.objects.filter()
            return Response({"detail": f""}, status=status.HTTP_200_OK)
        except (Exception, ) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)


class MerchantProductsView(APIView, CustomPagination):
    permission_classes = [IsAuthenticated, IsMerchant]

    def get(self, request):
        try:
            seller = Seller.objects.get(user=request.user)
            # products = Product.objects.filter(store__seller=seller)
            product_detail_query_set = ProductDetail.objects.filter(product__store__seller=seller).order_by('id')
            paginated_query_set = self.paginate_queryset(product_detail_query_set, request)
            serialized = MerchantProductDetailsSerializer(paginated_query_set, many=True).data
            serializer = self.get_paginated_response(serialized)
            return Response({"detail": serializer.data}, status=status.HTTP_200_OK)
        except (Exception, ) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)
