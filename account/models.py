from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from .choices import card_from_choices, address_type_choices


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_id = models.CharField(max_length=40, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile-pictures', null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=100, null=True, blank=True)
    code_expiration_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.user)

    def get_full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def first_name(self):
        return self.user.first_name

    def last_name(self):
        return self.user.last_name

    def email(self):
        return self.user.email


class UserCard(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    bank = models.CharField(max_length=50, null=True)
    card_from = models.CharField(max_length=50, null=True, choices=card_from_choices, default='paystack')
    card_type = models.CharField(max_length=50, null=True)
    bin = models.CharField(max_length=300, null=True)
    last4 = models.CharField(max_length=50, null=True)
    exp_month = models.CharField(max_length=2, null=True)
    exp_year = models.CharField(max_length=4, null=True)
    signature = models.CharField(max_length=200, null=True)
    authorization_code = models.CharField(max_length=200, null=True)
    payload = models.TextField(null=True)
    default = models.BooleanField(default=False, null=True)

    def __str__(self):
        return f"{self.id}: {self.profile}"


class ForgotPasswordOTP(models.Model):
    otp = models.SlugField(max_length=20, null=False, blank=False)
    email = models.EmailField(max_length=200, null=True)
    is_sent = models.BooleanField(help_text="If token was sent successfully", default=False)
    is_used = models.BooleanField(help_text="If token has been used", default=False)
    expire_time = models.DateTimeField(help_text="Expires after 5 minutes", blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class Address(models.Model):
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=address_type_choices, default='home')
    name = models.CharField(max_length=500)
    mobile_number = models.CharField(max_length=17)
    num = models.CharField(max_length=500)
    locality = models.CharField(max_length=500, blank=True, null=True)
    landmark = models.CharField(max_length=500, blank=True, null=True)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    town = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(default=0, blank=True, null=True, max_length=50)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    updated_on = models.DateTimeField(auto_now=True)

    def get_full_address(self):
        addr = ""
        if self.num:
            addr += f"{self.num}, "
        if self.locality:
            addr += f"{self.locality}, "
        if self.town:
            addr += f"{self.town}, "
        if self.city:
            addr += f"{self.city}, "
        if self.state:
            addr += f"{self.state}, "
        return addr.strip()

    def __str__(self):
        return "{} {} {}".format(self.type, self.name, self.locality)




