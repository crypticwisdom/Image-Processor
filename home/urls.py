from django.urls import path
from . import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='homepage'),
    path('banks/', views.ListAllBanksAPIView.as_view(), name='banks'),

    # webhooks
    path('payment-verify', views.OrderPaymentVerifyAPIView.as_view(), name='order-verify-payment'),

]


