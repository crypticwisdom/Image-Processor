from django.contrib.auth.models import User
from django.shortcuts import render

from module.email_service import send_email
from django.conf import settings


def shopper_signup_verification_email(email, profile):
    first_name = profile.user.first_name
    if not profile.user.first_name:
        first_name = "Payarena Shopper"

    message = f"Dear {first_name}, <br><br>Welcome to Payarena Mall. <br>Please click <a href='{settings.FRONTEND_VERIFICATION_URL}/{profile.verification_code}/'>here</a> to verify your email."
    subject = "Payarena Mall Email Verification"
    contents = render(None, 'default_template.html', context={'message': message}).content.decode('utf-8')
    send_email(contents, email, subject)
    return True


def shopper_welcome_email(email):
    first_name = User.objects.get(email=email).first_name

    if not first_name:
        first_name = "Payarena Shopper"

    message = str("Dear {name}, <br><br>Welcome to Payarena Mall. <br>Login to shop for amazing products "
                  "and discounts").format(name=str(first_name).title())
    subject = "Welcome to Payarena Mall"
    contents = render(None, 'default_template.html', context={'message': message}).content.decode('utf-8')

    send_email(contents, email, subject)
    return True
