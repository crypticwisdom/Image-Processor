from django.urls import path
from . import views

app_name = "account"

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='user-login'),   # POST
    path('sign-up/', views.SignupView.as_view(), name="sign-up"),   # POST
    path('forgot-password/', views.ForgotPasswordSendOTPView.as_view(), name="forgot-password"),   # GET and POST
    path('change-password/', views.ChangePasswordView.as_view(), name="change-password"),   # PUT


]

