from django.urls import path
from . import views

urlpatterns = [
    path('', views.MerchantView.as_view(), name='seller'),
    path('<int:seller_id>/', views.MerchantView.as_view(), name='seller-detail'),
    path('login/', views.MerchantLoginView.as_view(),)

]

