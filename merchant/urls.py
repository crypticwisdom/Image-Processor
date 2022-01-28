from django.urls import path
from . import views

urlpatterns = [
    path('seller/', views.SellerViews.as_view(), name='seller'),
    path('seller/<int:seller_id>/', views.SellerViews.as_view(), name='edit-delete-seller'),
    path('signin/', views.SignIn.as_view(),)

]

