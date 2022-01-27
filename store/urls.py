from django.urls import path
from store.views import (
    BrandView,
    ProductCategoryView,
    StoreView,
    ProductView,
    ProductDetailView,
    ProductImageView,
    ProductReviewView,
    ProductWishlistView,
    ShipperView,
    CartView,
    CartProductView,
    CartBillView,
)

app_name = 'store'

urlpatterns = [
    path('brands/', BrandView.as_view(), name='brands'),
    path('product_categories/', ProductCategoryView.as_view(), name='product_category'),
    path('store_view/', StoreView.as_view(), name='store_view'),
    path('products/', ProductView.as_view(), name='products'),
    path('products/<str:slug>/', ProductView.as_view(), name='products_detail'),
    path('product_image/', ProductImageView.as_view(), name='product_image'),
    path('product_review/', ProductReviewView.as_view(), name='product_review'),
    path('product_wishlist/', ProductWishlistView.as_view(), name='product_wishlist'),
    path('shippers/', ShipperView.as_view(), name='shippers'),
    path('carts/', CartView.as_view(), name='carts'),
    path('cart_product/', CartProductView.as_view(), name="cart_product"),
    path('cart_bill/', CartBillView.as_view(), name='cart_bill'),
]