from django.urls import path
from . import views

app_name = "account"

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='user-login'),
    path('sign-up/', views.SignupView.as_view(), name="sign-up"),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name="forgot-password"),   # GET and POST
]

