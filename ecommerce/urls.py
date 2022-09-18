from django.urls import path
from .views import MallLandPageView

app_name = "ecommerce"

urlpatterns = [
    path("", MallLandPageView.as_view(), name="mall-land-page"),

]