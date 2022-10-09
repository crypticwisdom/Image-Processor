from django.urls import path
from .views import MallLandPageView, AllCategoriesView, TopSellingProductsView, RecommendedProductView, \
    CartProductOperationsView, CartView

app_name = "ecommerce"

urlpatterns = [
    path("", MallLandPageView.as_view(), name="mall-land-page"),
    path("categories/", AllCategoriesView.as_view(), name="categories"),
    path("top-selling/", TopSellingProductsView.as_view(), name="top-selling"),
    path("recommended-products/", RecommendedProductView.as_view(), name="recommended-products"),
    path("cart-operation/", CartProductOperationsView.as_view(), name="add-to-cart"),
    path("cart-products/", CartView.as_view(), name="cart-products"),
]
