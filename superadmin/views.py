import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser

from account.utils import validate_email, register_payarena_user, create_account
from ecommerce.pagination import CustomPagination
from ecommerce.serializers import *

from account.serializers import *
from ecommerce.utils import top_monthly_categories
from home.utils import get_previous_date, get_month_start_and_end_datetime, get_year_start_and_end_datetime, \
    get_week_start_and_end_datetime
from merchant.models import Seller
from merchant.serializers import SellerSerializer
from merchant.utils import create_product, update_product, create_seller, update_seller
from store.serializers import ProductCategorySerializer
from superadmin.utils import create_or_update_category


class DashboardAPIView(APIView):
    permission_classes = []

    def get(self, request):
        # total_merchant, total_customer, total_product, sale_analysis, last_5_purchase_item, best_5_selling_product
        # best_selling_merchant_5, recent_payments
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")
        last_7_days = request.GET.get("last_7_days")
        this_month = request.GET.get("this_month")
        this_year = request.GET.get("this_year")
        this_week = request.GET.get("this_week")

        present_day = datetime.datetime.now()
        if last_7_days == "true":
            past_7_day = get_previous_date(date=present_day, delta=7)
            start_date = past_7_day
            end_date = present_day
        elif this_month == "true":
            month_start, month_end = get_month_start_and_end_datetime(present_day)
            start_date = month_start
            end_date = month_end
        elif this_year == "true":
            year_start, year_end = get_year_start_and_end_datetime(present_day)
            start_date = year_start
            end_date = year_end
        elif this_week == "true":
            week_start, week_end = get_week_start_and_end_datetime(present_day)
            start_date = week_start
            end_date = week_end
        else:
            start_date = date_from
            end_date = date_to

        data = dict()

        latest_purchased_products = OrderProduct.objects.all()[:5]
        best_selling_products = Product.objects.all().order_by("-sale_count")[:10]
        most_viewed_products = Product.objects.all().order_by("-view_count")[:10]

        if date_from and date_to:
            latest_purchased_products = OrderProduct.objects.filter(packed_on__range=(start_date, end_date))[:5]
            best_selling_products = Product.objects.filter(updated_on__range=(start_date, end_date)).order_by("-sale_count")[:10]
            most_viewed_products = Product.objects.filter(updated_on__range=(start_date, end_date)).order_by("-view_count")[:10]

        last_purchased = list()
        for order_product in latest_purchased_products:
            order = dict()
            order["order_id"] = order_product.id
            order["product_name"] = order_product.product_detail.product.name
            order["image"] = request.build_absolute_uri(order_product.product_detail.product.image.image.url)
            order["amount"] = order_product.total
            order["remaining_stock"] = order_product.product_detail.stock
            last_purchased.append(order)

        best_selling = list()
        for product in best_selling_products:
            prod = dict()
            prod["product_id"] = product.id
            prod["product_name"] = product.name
            prod["image"] = request.build_absolute_uri(product.image.image.url)
            prod["store_name"] = product.store.name
            prod["category_name"] = product.category.name
            prod["sale_count"] = product.sale_count
            best_selling.append(prod)

        most_viewed = list()
        for product in most_viewed_products:
            prod = dict()
            prod["product_id"] = product.id
            prod["product_name"] = product.name
            prod["image"] = request.build_absolute_uri(product.image.image.url)
            prod["store_name"] = product.store.name
            prod["category_name"] = product.category.name
            prod["view_count"] = product.view_count
            most_viewed.append(prod)

        data["last_purchases"] = last_purchased
        data["best_selling_products"] = best_selling
        data["most_viewed_products"] = most_viewed
        data["top_categories_for_the_month"] = top_monthly_categories()
        data["total_merchant"] = Seller.objects.all().count()
        data["total_customer"] = Profile.objects.all().count()
        data["total_product"] = Product.objects.all().count()

        return Response(data)


# Product Start
class ProductAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            return Response(ProductSerializer(Product.objects.get(id=pk), context={"request": request}).data)
        except Exception as err:
            return Response({"detail": "An error has occurred", "error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        merchant_id = request.data.get("seller_id")
        try:
            seller = Seller.objects.get(id=merchant_id)
            success, detail, product = create_product(request, seller)
            if success is False:
                return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": detail, "product": ProductSerializer(product, context={"request": request}).data})
        except Exception as err:
            return Response({"detail": "An error has occurred", "error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            product = Product.objects.get(id=pk)
            query = update_product(request, product)
            return Response({"detail": "Product updated successfully", "product": ProductSerializer(query, context={"request": request}).data})
        except Exception as ess:
            return Response({"detail": "An error has occurred", "error": str(ess)}, status=status.HTTP_400_BAD_REQUEST)


class ProductListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['store__name', 'name']

    def get_queryset(self):
        prod_status = self.request.GET.get("status")
        queryset = Product.objects.all().order_by("-id")
        if status:
            queryset = Product.objects.filter(status=prod_status).order_by("-id")
        return queryset

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
class BrandListAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = BrandSerializer
    queryset = Brand.objects.all().order_by("-id")
    pagination_class = CustomPagination


class BrandDetailRetrieveAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = BrandSerializer
    queryset = Brand.objects.all()
    lookup_field = "id"

# Brand End


# ProductCategory Start
class ProductCategoryListAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ProductCategorySerializer
    queryset = ProductCategory.objects.all().order_by('-id')
    pagination_class = CustomPagination

    def create(self, request, *args, **kwargs):
        data = dict()
        serializer = ProductCategorySerializer(data=request.data)
        if not serializer.is_valid():
            data['detail'] = 'Error in data sent'
            for key, value in serializer.errors.items():
                for text in value:
                    data['detail'] = f"Error in '{key}' sent: {text}"
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        category = create_or_update_category(data=request.data)
        return Response(ProductCategorySerializer(category, context={"request": request}).data)


class ProductCategoryDetailRetrieveAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ProductCategorySerializer
    queryset = ProductCategory.objects.all()
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        cat_id = self.kwargs.get("id")
        data = dict()
        serializer = ProductCategorySerializer(data=request.data)
        if not serializer.is_valid():
            data['detail'] = 'Error in data sent'
            for key, value in serializer.errors.items():
                for text in value:
                    data['detail'] = f"Error in '{key}' sent: {text}"
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        category = create_or_update_category(data=request.data, cat_id=cat_id)
        return Response(ProductCategorySerializer(category, context={"request": request}).data)

# ProductCategory End

# Merchant
class AdminSellerAPIView(APIView, CustomPagination):
    permission_classes = [IsAdminUser]

    def get(self, request, pk=None):
        if pk:
            serializer = SellerSerializer(Seller.objects.get(id=pk), context={"request": request})
        else:
            queryset = self.paginate_queryset(Seller.objects.all().order_by("-id"), request)
            data = SellerSerializer(queryset, many=True, context={"request": request}).data
            serializer = self.get_paginated_response(data)
        return Response(serializer.data)

    def put(self, request, seller_id):
        try:
            success, response = update_seller(request, seller_id)
            if success is False:
                return Response({"detail": response}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "Merchant account updated"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({"detail": "An error occurred while creating merchant", "error": str(ex)},
                            status=status.HTTP_400_BAD_REQUEST)

        ...

    def post(self, request):
        f_name = request.data.get("first_name")
        l_name = request.data.get("last_name")
        email = request.data.get("email")
        phone_number = request.data.get("phone_number")

        try:

            # create user and profile
            if not all([email, phone_number, f_name, l_name]):
                return Response({
                    "detail": "first name, last name, email, and phone number are required fields",
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check username exist
            if User.objects.filter(email=email).exists():
                return Response({"detail": "A user with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)

            if validate_email(email) is False:
                return Response({"detail": "Invalid Email Format"}, status=status.HTTP_400_BAD_REQUEST)

            phone_number = f"+234{phone_number[-10:]}"

            # Create account on payarena Auth Engine
            success, detail = register_payarena_user(email, phone_number, f_name, l_name, password)
            if success is False:
                return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)

            password = User.objects.make_random_password()

            success, response = create_account(email, phone_number, password, f_name, l_name)
            if success is False:
                return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
            user = response.user

            success, msg = create_seller(request, user, email, phone_number)
            if success is False:
                return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "Merchant account created"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({"detail": "An error occurred while creating merchant", "error": str(err)},
                            status=status.HTTP_400_BAD_REQUEST)







