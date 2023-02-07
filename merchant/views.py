from threading import Thread
from rest_framework.exceptions import ErrorDetail, ValidationError
from django.db.models import Q, F
from ecommerce.views import ProductReview
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from ecommerce.serializers import ProductSerializer, ReturnedProductSerializer
from account.utils import validate_email
from superadmin.exceptions import raise_serializer_error_msg
from transaction.models import Transaction
from transaction.serializers import TransactionSerializer
from .merchant_email import merchant_account_creation_email
from .serializers import SellerSerializer, MerchantProductDetailsSerializer, OrderSerializer, \
    MerchantDashboardOrderProductSerializer, MerchantReturnedProductSerializer, MerchantBannerSerializerOut, \
    MerchantBannerSerializerIn, MerchantProductReviewSerialiazer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, generics
from home.pagination import CustomPagination
from .utils import *
from .permissions import IsMerchant
from ecommerce.models import ProductDetail, Product, ProductCategory, OrderProduct, Order
from django_filters import rest_framework as filters
from .filters import MerchantOrderProductFilter
from services import utils


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
                phone_number = f"{234}{phone_number[-10:]}"
            else:
                return Response({"detail": "Phone Number is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Create Merchant for Authenticated User
            if user is not None and request.user.is_authenticated:
                if Seller.objects.filter(user=user).exists():
                    return Response({"detail": "You already have a merchant account"},
                                    status=status.HTTP_400_BAD_REQUEST)

            success, msg = create_seller(request, user, email, phone_number)

            if not success:
                return Response({"detail": f"{msg}"}, status=status.HTTP_400_BAD_REQUEST)
            Thread(target=merchant_account_creation_email, args=[email]).start()
            return Response({"detail": f"{msg}."})
        except (Exception,) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)


class MerchantDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsMerchant]

    def get(self, request):
        try:
            store = Store.objects.get(seller__user=request.user)
            return Response({"detail": get_dashboard_data(store, request)})
        except (Exception,) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)


# Added Search by product_name and category(filter).
class ProductAPIView(APIView, CustomPagination):

    def get(self, request, pk=None):
        try:
            product_name, category = request.GET.get("product_name", None), request.GET.get("category", None)
            seller = Seller.objects.get(user=request.user)
            query = Q(store__seller=seller)

            if pk:
                serializer = ProductSerializer(Product.objects.get(store__seller=seller, id=pk),
                                               context={"request": request}).data
            else:
                if product_name:
                    query &= Q(name__icontains=product_name)

                if category:
                    query &= Q(category__name__icontains=category)

                product_detail_query_set = Product.objects.filter(query).order_by('-id')
                paginated_query_set = self.paginate_queryset(product_detail_query_set, request)
                serialized = ProductSerializer(paginated_query_set, many=True, context={"request": request}).data
                serializer = self.get_paginated_response(serialized).data
            return Response(serializer)
        except (Exception,) as err:
            return Response({"detail": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            if not Seller.objects.filter(user=request.user).exists():
                return Response({"detail": "Only merchant account can add product"}, status=status.HTTP_400_BAD_REQUEST)
            seller = Seller.objects.get(user=request.user)
            success, detail, product = create_product(request, seller)
            if success is False:
                return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
            return Response(
                {"detail": detail, "product": ProductSerializer(product, context={"request": request}).data})
        except Exception as err:
            return Response({"detail": "An error has occurred", "error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            store = Store.objects.get(seller__user=request.user)
            product = Product.objects.get(id=pk, store=store)
            query = update_product(request, product)
            return Response({"detail": "Product updated successfully",
                             "product": ProductSerializer(query, context={"request": request}).data})
        except Exception as ess:
            return Response({"detail": "An error has occurred", "error": str(ess)}, status=status.HTTP_400_BAD_REQUEST)


# Haven't written this "Ashavin said it should be handled by the Admin"
class MerchantAddBannerView(APIView):
    permission_classes = [IsAuthenticated, IsMerchant]

    def post(self, request):
        try:
            # Get image from the F.E.
            # Process Image (Banner): Must be a certain size.
            #
            return Response({"detail": "..."})
        except (Exception,) as err:
            return Response({"detail": str(err)}, status=status.HTTP_400_BAD_REQUEST)


class MerchantOrderProductsView(generics.ListAPIView):
    """
        filter_backends: used to specify Django Default FilterSet which creates a FilterSet based on 'filterset_fields'.
        filterset_class: Used to pass in your written customized FilterSet class, don't use 'filterset_fields' with it.
        filterset_fields: Used to specify the field name to filter against in the Model.

        Note: The DjangoFilterBackend is not neccessary in the 'filter_backends' if we already passed in our custom
            FilterSet in filter_class.
    """
    permission_classes = [IsAuthenticated, IsMerchant]
    pagination_class = CustomPagination
    serializer_class = MerchantDashboardOrderProductSerializer
    # filter_backends = [filters.DjangoFilterBackend]
    filterset_class = MerchantOrderProductFilter

    def get_queryset(self):
        query = Q(product_detail__product__store__seller__user=self.request.user)

        start_date = self.request.GET.get("date_from", None)
        end_date = self.request.GET.get("date_to", None)
        status_ = self.request.GET.get("status", None)

        if (start_date is not None and end_date is None) or (end_date is not None and start_date is None):
            # Check if both 'start' and 'end' are both given.
            raise ValidationError({'detail': "Filter by Date Range requires both start_date and end_date."})

        if start_date is not None and end_date is not None:
            if status_ == "cancelled":
                query &= Q(cancelled_on__date__range=[start_date, end_date])
            elif status_ == "paid":
                query &= Q(payment_on__date__range=[start_date, end_date])
            elif status_ == "delivered":
                query &= Q(delivered_on__date__range=[start_date, end_date])
            elif status_ == "returned":
                query &= Q(returned_on__date__range=[start_date, end_date])
            elif status_ == "processed":
                query &= Q(packed_on__date__range=[start_date, end_date])
            elif status_ == "shipped":
                query &= Q(shipped_on__date__range=[start_date, end_date])
            elif status_ == "pending":  # What should be the pending status ...
                query &= Q(returned_on__date__range=[start_date, end_date])
            elif status_ == "refunded":
                query &= Q(refunded_on__date__range=[start_date, end_date])
            else:
                query &= Q(created_on__range=[start_date, end_date])

        queryset = OrderProduct.objects.filter(query).order_by('-id')
        return queryset


# Completed [Filter is pending ...]
class MerchantLowAndOutOfStockView(APIView, CustomPagination):
    permission_classes = [IsAuthenticated, IsMerchant]

    def get(self, request):
        try:
            stock_type = request.GET.get("stock_type", None)

            # filter_by_date_from, filter_by_date_to = request.GET.get("date_from", None), request.GET.get("date_to", None)
            # filter_by_status = request.GET.get("status", None)
            # category_id = request.GET.get("category_id", None)

            if stock_type is None:
                return Response({"detail": f"Stock Type is required."}, status=status.HTTP_400_BAD_REQUEST)

            store, query_set = Store.objects.get(seller__user=request.user), None
            if stock_type in ["low_in_stock", "low"]:
                query_set = ProductDetail.objects.filter(product__store=store,
                                                         low_stock_threshold__gt=F('stock'), stock__gte=1).order_by(
                    '-id')
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
            query_set = ReturnedProduct.objects.filter(
                product__product_detail__product__store__seller__user=request.user,
                status="approved").order_by("-id")

            paginated_query_set = self.paginate_queryset(query_set, request)
            serialized_data = MerchantReturnedProductSerializer(paginated_query_set, many=True,
                                                                context={"request": request}).data
            response = self.get_paginated_response(serialized_data).data
            return Response({"detail": response})
        except (Exception,) as err:
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
        except (Exception,) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)


class ProductImageView(APIView):
    def post(self, request):
        try:
            image = request.data.getlist('image')

            if len(image) > 1:
                # Making sure that the number of image this end point receives is just 1 image.
                return Response({"detail": "You can only provide 1 image."},
                                status=status.HTTP_400_BAD_REQUEST)
            image = image[0]
            success, msg = utils.image_processor(2, image=image)

            if success is False:
                return Response({"detail": f"{msg}"}, status=status.HTTP_400_BAD_REQUEST)

            img = Image.objects.create(image=image)
            return Response({"detail": "Image uploaded successfully", "image_id": img.id,
                             "image_url": request.build_absolute_uri(img.image.url)})
        except Exception as ex:
            return Response({"detail": f"{str(ex)}"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not Image.objects.filter(id=pk).exists():
            return Response({'detail': 'Image does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        Image.objects.get(id=pk).delete()
        return Response({'detail': 'Image deleted successfully'})


class MerchantTransactionAPIView(APIView, CustomPagination):
    def get(self, request, pk=None):
        merchant = Seller.objects.get(user=request.user)
        store = Store.objects.get(seller=merchant)
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")
        search = request.GET.get("search")
        status = request.GET.get("status")

        if pk:
            serializer = TransactionSerializer(
                Transaction.objects.get(id=pk, order__orderproduct__product_detail__product__store=store
                                        ), context={"merchant": merchant}).data
        else:
            query = Q(order__orderproduct__product_detail__product__store=store)
            if search:
                query &= Q(order__orderproduct__product_detail__product__name=search) | \
                         Q(order__orderproduct__product_detail__product__category__name=search) | \
                         Q(order__customer__user__first_name=search) | Q(order__customer__user__last_name=search)
            if status:
                query &= Q(status=status)
            if date_from and date_to:
                query &= Q(created_on__range=[date_from, date_to])

            queryset = self.paginate_queryset(Transaction.objects.filter(query), request)
            data = TransactionSerializer(queryset, many=True, context={"merchant": merchant}).data
            serializer = self.get_paginated_response(data).data

        return Response(serializer)


class MerchantBannerListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated & (IsAdminUser | IsMerchant)]
    serializer_class = MerchantBannerSerializerOut
    pagination_class = CustomPagination

    def get_queryset(self):
        if self.request.user.is_staff:
            return MerchantBanner.objects.all().order_by("-id")
        seller = get_object_or_404(Seller, user=self.request.user)
        return MerchantBanner.objects.filter(seller=seller).order_by("-id")

    def create(self, request, *args, **kwargs):
        try:

            # Image processor implementation
            image = request.data.getlist('image')[0]
            success, msg = utils.image_processor(8, image)
            if not success:
                return Response({"detail": f"{msg}"}, status=status.HTTP_400_BAD_REQUEST)
            # Implementation ends here

            serializer = MerchantBannerSerializerIn(data=request.data, context=self.get_serializer_context())
            serializer.is_valid() or raise_serializer_error_msg(errors=serializer.errors)
            serializer = serializer.save()
            return Response({"detail": "Banner added successfully", "data": serializer})
        except (Exception, ) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)

class MerchantBannerRetrieveUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated & (IsAdminUser | IsMerchant)]
    serializer_class = MerchantBannerSerializerOut
    lookup_field = "id"

    def get_queryset(self):
        if self.request.user.is_staff:
            return get_object_or_404(MerchantBanner, id=self.kwargs.get("id"))
        return MerchantBanner.objects.get(id=self.kwargs.get("id"), seller__user=self.request.user)

    def update(self, request, *args, **kwargs):
        serializer = MerchantBannerSerializerIn(data=request.data, instance=self.kwargs.get("id"),
                                                context=self.get_serializer_context())
        serializer.is_valid() or raise_serializer_error_msg(errors=serializer.errors)
        serializer.save()
        return Response({"detail": "Banner updated successfully", "data": serializer})


class ProductImageAPIView(APIView):
    def post(self, request):
        try:
            image = request.data.get('image')
            success, msg = utils.image_processor(2, image=image)

            if not success:
                return Response({"detail": f"{msg}"}, status=status.HTTP_400_BAD_REQUEST)

            product_image = Image.objects.create(image=image)

            return Response({"detail": "Image has been uploaded successfully", "image_id": product_image.id,
                             "image_url": product_image.image.url})
        except Exception as ex:
            return Response(
                {"detail": "An error occurred. Please try again", "error": str(ex)},
                status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not Image.objects.filter(id=pk).exists():
            return Response({'detail': 'Image does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        Image.objects.get(id=pk).delete()
        return Response({'detail': 'Image deleted successfully'})


class MerchantProductReviewsView(APIView, CustomPagination):
    permission_classes = [IsAuthenticated, IsMerchant]

    def get(self, request, pk=None):
        try:
            merchant_store = Store.objects.get(seller__user=request.user)
            if pk:
                reviews = ProductReview.objects.get(id=pk, product__store=merchant_store)
                data = MerchantProductReviewSerialiazer(reviews, context={"request": request}).data
                return Response({"detail": data})

            if pk is None:
                reviews = ProductReview.objects.filter(product__store=merchant_store).order_by("-id")
                queryset = self.paginate_queryset(reviews, request)
                data = MerchantProductReviewSerialiazer(queryset, context={"request": request}, many=True).data
                serializer = self.get_paginated_response(data).data

                return Response({"detail": serializer})
        except (Exception,) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)
