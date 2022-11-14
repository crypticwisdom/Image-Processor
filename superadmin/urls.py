from django.urls import path
from . import views

app_name = "superadmin"

urlpatterns = [
    path("", views.DashboardAPIView.as_view(), name="dashboard"),

]

