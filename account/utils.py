import re

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from account.models import Profile


def create_account(username, email, phone_number, password):
    try:
        user_instance = User.objects.create(username=username, email=email, password=make_password(password))
        if user_instance:
            profile = Profile.objects.create(user=user_instance, phone_number=phone_number)
            if not profile:
                return False, "An error occurred while creating a profile for this user"
            return True, profile
        else:
            return False, "User not created"
    except (Exception, ) as err:
        # Log error
        print(err)
        return False, "An error occurred during user creation"


def validate_email(email, /):
    try:
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(regex, email):
            return True
        return False
    except (TypeError, Exception) as err:
        # Log error
        return False
