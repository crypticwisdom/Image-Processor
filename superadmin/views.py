import datetime

from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser

from ecommerce.pagination import CustomPagination
from ecommerce.serializers import *

from account.serializers import *
from ecommerce.utils import top_monthly_categories
from home.utils import get_previous_date, get_month_start_and_end_datetime, get_year_start_and_end_datetime, \
    get_week_start_and_end_datetime
from merchant.models import Seller
from store.serializers import ProductCategorySerializer


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
class ProductListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    serializer_class = [ProductSerializer]
    queryset = Product.objects.all().order_by("-id")


class ProductRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = [ProductSerializer]
    queryset = Product.objects.all()
    lookup_field = "id"
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
class BrandListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = BrandSerializer
    queryset = Brand.objects.all().order_by("-id")
    pagination_class = CustomPagination


class BrandDetailRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = BrandSerializer
    queryset = Brand.objects.all()
    lookup_field = "id"

# Brand End

# ProductCategory Start
class ProductCategoryListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ProductCategorySerializer
    queryset = ProductCategory.objects.all().order_by('-id')
    pagination_class = CustomPagination


class ProductCategoryDetailRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ProductCategorySerializer
    queryset = ProductCategory.objects.all()
    lookup_field = "id"

# ProductCategory End

