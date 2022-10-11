from django.contrib import admin
from account.models import Profile, ForgotPasswordOTP, Address


class AddressStackInlineAdmin(admin.TabularInline):
    model = Address


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "phone_number"]
    search_fields = ["user__first_name", "user__email"]
    list_filter = ["created_on"]
    inlines = [AddressStackInlineAdmin]


admin.site.register(Profile, ProfileAdmin)
admin.site.register(ForgotPasswordOTP)
