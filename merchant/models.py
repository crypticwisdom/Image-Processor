from django.db import models
from django.contrib.auth.models import User

from location.models import City, State, Country
from .choices import *


class Seller(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.ForeignKey(City, null=True, on_delete=models.SET_NULL, blank=True)
    state = models.ForeignKey(State, null=True, on_delete=models.SET_NULL, blank=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.SET_NULL, blank=True)
    status = models.CharField(max_length=20, choices=seller_status_choices, default='pending')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user}-{self.phone_number}: {self.status}'


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




