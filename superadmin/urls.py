from django.urls import path
from . import views

app_name = "superadmin"

urlpatterns = [
    path("", views.DashboardAPIView.as_view(), name="dashboard"),

    # Categories
    path("categories/", views.ProductCategoryListAPIView.as_view(), name=""),
    path("categories/<int:id>/", views.ProductCategoryDetailRetrieveAPIView.as_view(), name=""),

    # Brands
    path("brand/", views.BrandListAPIView.as_view(), name=""),
    path("brand/<int:id>/", views.BrandDetailRetrieveAPIView.as_view(), name=""),

    # Product
    path("products", views.ProductListAPIView.as_view(), name="product"),
    path("products/", views.ProductAPIView.as_view(), name="product"),
    path("products/<int:pk>/", views.ProductAPIView.as_view(), name="product-detail"),

    # Merchant
    path("seller/", views.AdminSellerAPIView.as_view(), name="seller"),
    path("seller/<int:pk>/", views.AdminSellerAPIView.as_view(), name="seller-detail"),

]

