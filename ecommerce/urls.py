from django.urls import path
from .views import MallLandPageView, AllCategoriesView, TopSellingProductsView, RecommendedProductView

app_name = "ecommerce"

urlpatterns = [
    path("", MallLandPageView.as_view(), name="mall-land-page"),
    path("categories/", AllCategoriesView.as_view(), name="categories"),
    path("top-selling/", TopSellingProductsView.as_view(), name="top-selling"),
    path("recommended-products/", RecommendedProductView.as_view(), name="recommended-products"),

]