from django.urls import path
from . import views

urlpatterns = [
    path('', views.MerchantView.as_view(), name='seller'),
    path('<int:seller_id>/', views.MerchantView.as_view(), name='seller-detail'),
    path('login/', views.MerchantLoginView.as_view(),),
    path('create-merchant/', views.BecomeAMerchantView.as_view(), name="create-merchant"),
    path('dashboard/', views.MerchantDashboardView.as_view(), name="merchant-dashboard"),
    path('products/', views.ProductAPIView.as_view(), name="product"),
]

