from django.urls import path
from . import views

app_name = "superadmin"

urlpatterns = [
    path("", views.DashboardAPIView.as_view(), name="dashboard"),
    path("categories/", views.ProductCategoryListAPIView.as_view(), name=""),

]

