from django.db.models import Q, F
from rest_framework.permissions import IsAuthenticated
from ecommerce.serializers import ProductSerializer, ReturnedProductSerializer
from account.utils import validate_email
from transaction.models import Transaction
from .serializers import SellerSerializer, MerchantProductDetailsSerializer, OrderSerializer, \
    MerchantDashboardOrderProductSerializer, MerchantReturnedProductSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from home.pagination import CustomPagination
from .utils import *
from .permissions import IsMerchant
from ecommerce.models import ProductDetail, Product, ProductCategory, OrderProduct, Order
from rest_framework.generics import ListAPIView
from django_filters import rest_framework as filters
from .filters import MerchantOrderProductFilter


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
            return Response({"detail": get_dashboard_data(store, request)})
        except (Exception, ) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)


class ProductAPIView(APIView, CustomPagination):

    def get(self, request):
        try:
            seller = Seller.objects.get(user=request.user)
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


# Haven't written this "Ashavin said it should be handle by the Admin"
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


# The date range filter is not working as expected.  filter by status and category id works.
# class MerchantOrdersView(APIView, CustomPagination):
#     permission_classes = [IsAuthenticated, IsMerchant]
#
#     def get(self, request, name=None):
#         try:
#
#             filter_by_date_from, filter_by_date_to = request.GET.get("date_from", None), request.GET.get("date_to", None)
#             filter_by_status = request.GET.get("status", None)
#             category_id = request.GET.get("category_id", None)
#
#             # Get Store instance for this user.
#             query = Q(product_detail__product__store__seller__user=request.user)
#
#             # if category_id is not None:
#             #     query &= Q(product_detail__product__category=category_id)
#
#             # if filter_by_status:
#             #     query &= Q(status=filter_by_status)
#
#             if filter_by_date_from is not None and filter_by_date_to is not None:
#                 # Not really working as expected, will check later
#                 query &= Q(delivered_on__range=[filter_by_date_from, filter_by_date_to])
#                 query &= Q(shipped_on__range=[filter_by_date_from, filter_by_date_to])
#                 query &= Q(returned_on__range=[filter_by_date_from, filter_by_date_to])
#                 query &= Q(payment_on__range=[filter_by_date_from, filter_by_date_to])
#                 query &= Q(refunded_on__range=[filter_by_date_from, filter_by_date_to])
#                 query &= Q(packed_on__range=[filter_by_date_from, filter_by_date_to])
#                 query &= Q(cancelled_on__range=[filter_by_date_from, filter_by_date_to])
#                 query &= Q(created_on__range=[filter_by_date_from, filter_by_date_to])
#
#             orders = OrderProduct.objects.filter(query).order_by("-id")
#             paginated_query_set = self.paginate_queryset(orders, request)
#             serializer = MerchantDashboardOrderProductSerializer(instance=paginated_query_set, many=True).data
#             paginated_serializer = self.get_paginated_response(serializer).data
#
#             return Response(paginated_serializer)
#         except (Exception, ) as err:
#             return Response({"detail": f"{err}d"}, status=status.HTTP_400_BAD_REQUEST)


class MerchantOrdersView(ListAPIView):
    permission_classes = [IsAuthenticated, IsMerchant]
    queryset = OrderProduct.objects.all().order_by("-id")
    pagination_class = CustomPagination
    serializer_class = MerchantDashboardOrderProductSerializer
    filter_backends = (filters.DjangoFilterBackend, )
    filterset_class = MerchantOrderProductFilter
    # filterset_fields = {
    #     'cancelled_on': ['cancelled_on__date']
    # }

    # def get_queryset(self):
    #     # queryset = OrderProduct.objects.filter(product_detail__product__store__user=self.request.user).order_by("-id")
    #     print('queryset')
    #     return 'queryset'


# Completed
class LowAndOutOfStockView(APIView, CustomPagination):
    permission_classes = [IsAuthenticated, IsMerchant]

    def get(self, request):
        try:
            stock_type = request.data.get("stock_type", None)

            if stock_type is None:
                return Response({"detail": f"Stock Type is required."}, status=status.HTTP_400_BAD_REQUEST)

            store, query_set = Store.objects.get(seller__user=request.user), None
            if stock_type in ["low_in_stock", "low"]:
                query_set = ProductDetail.objects.filter(product__store=store,
                                                         low_stock_threshold__gte=F('stock')).order_by('-id')
            elif stock_type in ["out_of_stock", "out"]:
                query_set = ProductDetail.objects.filter(product__store=store, stock__lte=0).order_by('-id')
            else:
                return Response({"detail": f"Invalid stock type value passed."}, status=status.HTTP_400_BAD_REQUEST)

            paginated_query_set = self.paginate_queryset(query_set, request)
            serialized_data = ProductLowAndOutOffStockSerializer(paginated_query_set, many=True,
                                                                 context={"request": request}).data
            response = self.get_paginated_response(serialized_data).data

            return Response({"detail": response})
        except (Exception, TypeError) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)


# Completed.
class MerchantReturnsAndRejectView(APIView, CustomPagination):
    permission_classes = [IsAuthenticated, IsMerchant]

    def get(self, request):
        try:
            # Filter all ReturnedProduct where this Merchant is the owner of the Store.
            query_set = ReturnedProduct.objects.filter(product__product_detail__product__store__seller__user=request.user,
                                                       status="approved").order_by("-id")

            paginated_query_set = self.paginate_queryset(query_set, request)
            serialized_data = MerchantReturnedProductSerializer(paginated_query_set, many=True,
                                                                context={"request": request}).data
            response = self.get_paginated_response(serialized_data).data
            return Response({"detail": response})
        except (Exception, ) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)


class MerchantTransactionView(APIView, CustomPagination):
    permission_classes = [IsAuthenticated, IsMerchant]

    def get(self, request):
        try:
            query = request.GET.get("query", None)  # filter by, product name, customer name ...
            q_status = request.GET.get("status", None)  # filter by, successful cancel ...
            print(query)
            if query is not None:
                # How would i get all Transactions related to this Current Logged in Merchant ?
                transactions = Transaction.objects.filter()
            return Response({"detail": f""})
        except (Exception, ) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)
