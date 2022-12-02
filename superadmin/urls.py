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
    path("seller/<int:seller_id>/", views.AdminSellerAPIView.as_view(), name="seller-detail"),
    path("merchant-status/", views.UpdateMerchantStatusAPIView.as_view(), name="merchant-status"),

    # Admin Users
    path("login/", views.AdminSignInAPIView.as_view(), name="admin-login"),
    path("admins/", views.AdminUserListCreateAPIView.as_view(), name="admin-user"),
    path("admins/<int:id>/", views.AdminUserRetrieveUpdateAPIView.as_view(), name="admin-user-detail"),

    # Banner/Promo
    path("banner-promo/", views.AdminBannerView.as_view(), name="banner"),
    path("banner-promo/<int:id>/", views.BannerDetailView.as_view(), name="banner-detail"),

    # Transaction
    path("transaction/", views.AdminTransactionListAPIView.as_view(), name="transactions"),
    path("transaction/<int:id>/", views.AdminTransactionRetrieveAPIView.as_view(), name="transaction-detail"),

    # Customers
    path("customer/", views.ProfileListAPIView.as_view(), name="customer"),
    path("customer/<int:id>/", views.ProfileDetailRetrieveAPIView.as_view(), name="customer-detail"),

    # Orders
    path('orders/', views.OrdersView.as_view(), name="orders"),
    path('orders/<str:param>/', views.OrdersView.as_view(), name="orders"),
    path('order/<int:order_product_id>/', views.OrderDetailView.as_view(), name='order'),

]

