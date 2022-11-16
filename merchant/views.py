from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from ecommerce.serializers import ProductSerializer
from account.utils import validate_email
from .serializers import SellerSerializer, MerchantProductDetailsSerializer, OrderSerializer, \
    MerchantDashboardOrderProductSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from home.pagination import CustomPagination
from .utils import *
from .permissions import IsMerchant
from ecommerce.models import ProductDetail, Product, ProductCategory, OrderProduct, Order


class MerchantView(APIView, CustomPagination):
    permission_classes = []

    def get(self, request, seller_id=None):

        try:
            if seller_id:
                item = Seller.objects.get(id=seller_id)
                serializer = SellerSerializer(item)
            else:
                paginated_query_set = self.paginate_queryset(Seller.objects.all(), request)
                serializer = SellerSerializer(paginated_query_set, many=True).data
                serializer = self.get_paginated_response(serializer)
            return Response(serializer.data)
        except Exception as ex:
            return Response({"detail": "Error getting object", "message": str(ex)},
                            status=status.HTTP_400_BAD_REQUEST)


class BecomeAMerchantView(APIView):
    permission_classes = [IsAuthenticated]

    """
        Authenticated users are allowed to call this endpoint.
    """

    def post(self, request):
        try:
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
                return Response({"detail": "Phone Number is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Create Merchant for Authenticated User
            if user is not None and request.user.is_authenticated:
                if Seller.objects.filter(user=user).exists():
                    return Response({"detail": "You already have a merchant account"},
                                    status=status.HTTP_400_BAD_REQUEST)

                success, msg = create_seller(request, user, email, phone_number)

                if not success:
                    return Response({"detail": f"{msg}"})

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

            return Response({"detail": f"{msg}."})
        except (Exception,) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)


class MerchantDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsMerchant]

    def get(self, request):
        try:
            store = Store.objects.get(seller__user=request.user)
            return Response({"detail": get_dashboard_data(store)})
        except (Exception, ) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)


class ProductAPIView(APIView, CustomPagination):

    def get(self, request):
        try:
            seller = Seller.objects.get(user=request.user)
            # products = Product.objects.filter(store__seller=seller)
            product_detail_query_set = ProductDetail.objects.filter(product__store__seller=seller).order_by('-id')
            paginated_query_set = self.paginate_queryset(product_detail_query_set, request)
            serialized = MerchantProductDetailsSerializer(paginated_query_set, many=True, context={"request": request}).data
            serializer = self.get_paginated_response(serialized)
            return Response({"detail": serializer.data})
        except (Exception, ) as err:
            return Response({"detail": str(err)}, status=status.HTTP_400_BAD_REQUEST)

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


class MerchantAddBannerView(APIView):
    permission_classes = [IsAuthenticated, IsMerchant]

    def post(self, request):
        try:
            # Get image from the F.E.
            # Process Image (Banner): Must be a certain size.
            #
            return Response({"detail": "..."})
        except (Exception, ) as err:
            return Response({"detail": str(err)}, status=status.HTTP_400_BAD_REQUEST)


class MerchantOrdersView(APIView):
    permission_classes = [IsAuthenticated, IsMerchant]

    def get(self, request, name=None):
        try:
            filter_by_date, filter_by_status = request.GET.get("date", None), request.GET.get("date", None)

            # if filter_by_status and filter_by_date:
            #     Q(created_on=)
            print(request.user, request.user.profile)
            orders = OrderProduct.objects.filter(order__customer=request.user.profile)
            print(orders)
            # sserializer = OrderProductSerializer()
            serializer = MerchantDashboardOrderProductSerializer(instance=orders, many=True).data
            return Response({"detail": serializer})
        except (Exception, ) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)
