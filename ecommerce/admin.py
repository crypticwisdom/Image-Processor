from django.contrib import admin
from ecommerce.models import Promo, ProductType, Image, OrderProduct, Order


class OrderProductTabularInlineAdmin(admin.TabularInline):
    model = OrderProduct


class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "payment_status"]
    list_filter = ["payment_status", "shipper_name"]
    inlines = [OrderProductTabularInlineAdmin]


admin.site.register(Promo)
admin.site.register(Image)
admin.site.register(ProductType)
admin.site.register(Order, OrderAdmin)
