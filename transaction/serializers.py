from rest_framework import serializers

from ecommerce.models import Order, OrderProduct
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    order_detail = serializers.SerializerMethodField()

    def get_order_detail(self, obj):
        data = dict()
        order = Order.objects.get(id=obj.id)
        data["order_id"] = order.id
        waybills = list()
        product_name_list = list()
        product_category_list = list()
        seller_list = list()
        for order_products in OrderProduct.objects.filter(order=order):
            product_name_list.append(order_products.product_detail.product.name)
            product_category_list.append(order_products.product_detail.product.category.name)
            seller_list.append(str(order_products.product_detail.product.store.seller.id))
            waybills.append(order_products.waybill_no)

        data["product_names"] = ", ".join(set(product_name_list))
        data["categories"] = ", ".join(set(product_category_list))
        data["seller_id"] = ", ".join(set(seller_list))
        data["waybill_no"] = ", ".join(set(waybills))

        return data

    class Meta:
        model = Transaction
        exclude = ["order"]



