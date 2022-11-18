from django.contrib import admin
from ecommerce.models import Promo, ProductType, Image, OrderProduct, Order, ReturnReason, ReturnedProduct, \
    ReturnProductImage, Address, ProductWishlist


class OrderProductTabularInlineAdmin(admin.TabularInline):
    model = OrderProduct


class OrderProductModelAdmin(admin.ModelAdmin):
    model = OrderProduct
    list_filter = ["status"]


class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "payment_status"]
    list_filter = ["payment_status"]
    inlines = [OrderProductTabularInlineAdmin]


admin.site.register(Promo)
admin.site.register(ProductWishlist)
admin.site.register(Address)
admin.site.register(Image)
admin.site.register(ProductType)
admin.site.register(ReturnReason)
admin.site.register(ReturnedProduct)
admin.site.register(ReturnProductImage)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductModelAdmin)
