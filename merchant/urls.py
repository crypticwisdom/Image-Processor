from django.urls import path
from . import views

urlpatterns = [
    path('', views.MerchantView.as_view(), name='seller'),
    path('<int:seller_id>/', views.MerchantView.as_view(), name='seller-detail'),
    path('create-merchant/', views.BecomeAMerchantView.as_view(), name="create-merchant"),
    path('add-banner/', views.MerchantAddBannerView.as_view(), name="add-banner"),
    path('dashboard/', views.MerchantDashboardView.as_view(), name="merchant-dashboard"),
    path('products/', views.ProductAPIView.as_view(), name="product"),
    path('products/<int:pk>/', views.ProductAPIView.as_view(), name="product"),

    path('product/image/', views.ProductImageView.as_view(), name="product-image"),

    # Orders
    path('orders/', views.MerchantOrdersView.as_view(), name="merchant-orders"),

    # Transactions
    path('transaction', views.MerchantTransactionAPIView.as_view(), name="transaction"),
    path('transaction/<int:pk>/', views.MerchantTransactionAPIView.as_view(), name="transaction-detail"),

]

