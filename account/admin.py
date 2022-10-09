from django.contrib import admin
from account.models import Profile, ForgotPasswordOTP
# Register your models here.
admin.site.register(Profile)
admin.site.register(ForgotPasswordOTP)
