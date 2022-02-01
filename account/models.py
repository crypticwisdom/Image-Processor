from django.contrib.auth.models import User
from django.db import models

from .choices import card_from_choices
from location.models import Country, State, City


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    home_address = models.CharField(max_length=100, null=True, blank=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.SET_NULL, blank=True)
    state = models.ForeignKey(State, null=True, on_delete=models.SET_NULL, blank=True)
    city = models.ForeignKey(City, null=True, on_delete=models.SET_NULL, blank=True)
    profile_picture = models.ImageField(upload_to='profile-pictures', null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)

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
    email = models.EmailField()
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
