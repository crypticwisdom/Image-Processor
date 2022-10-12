from django.contrib.auth.models import User
from django.shortcuts import render

from module.email_service import send_email


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
