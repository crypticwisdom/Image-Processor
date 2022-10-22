from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

# from location.models import City, State, Country
from .choices import *


# token = Token.objects.create(user=User.objects.get(pk=1))
# print(token.key)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Seller(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    town = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    profile_picture = models.ImageField(null=True, blank=True, upload_to='seller-profile-picture')
    status = models.CharField(max_length=20, choices=seller_status_choices, default='pending', null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user}-{self.phone_number}: {self.status}'

    def get_full_address(self):
        addr = ""
        if self.address:
            addr += f"{self.address}, "
        if self.town:
            addr += f"{self.town}, "
        if self.city:
            addr += f"{self.city}, "
        if self.state:
            addr += f"{self.state}, "
        return addr.strip()


class SellerVerification(models.Model):
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE)
    id_card = models.ImageField(null=True, blank=True, upload_to='seller-verification')
    id_card_verified = models.BooleanField(default=False)
    cac_number = models.CharField(null=True, blank=True, max_length=15)
    cac_verified = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.seller}: {self.verified}'


class SellerFile(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    file = models.FileField(upload_to='seller-files')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.seller}: {self.file}'




