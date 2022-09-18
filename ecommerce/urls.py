from django.urls import path
from .views import MallLandPageView, AllCategoriesView

app_name = "ecommerce"

urlpatterns = [
    path("", MallLandPageView.as_view(), name="mall-land-page"),
    path("categories/", AllCategoriesView.as_view(), name="categories"),

]