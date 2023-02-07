from .views import GetView
from django.urls import path

app_name = "management"

urlpatterns = [
    path('get', GetView.as_view(), name="get-all-content-types")
]