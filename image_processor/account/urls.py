from django.urls import path
from account import views

app_name = "account"

urlpatterns = [
    path("register", views.RegisterView.as_view(), name="register"),
    path("login", views.LoginView.as_view(), name="login"),
    path("update-profile", views.UpdateProfileView.as_view(), name="update_profile"),
    path("blocks", views.GetClientsValidationBlocks.as_view(), name="all-blocks"),
]
