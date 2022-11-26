from django_filters import rest_framework as filters
from ecommerce.models import ProductDetail, Product, ProductCategory, OrderProduct, Order


class MerchantOrderProductFilter(filters.FilterSet):
    status = filters.CharFilter(field_name="status", lookup_expr="iexact")
    cancelled_on = filters.DateFromToRangeFilter(field_name="cancelled_on")

    class Meta:
        model = OrderProduct
        fields = ['status', 'cancelled_on']
