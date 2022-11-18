from module.email_service import send_email


def forgot_password_mail(email, forgot_password_instance):
    """
    :param forgot_password_instance:
    :param email:
    :return: None:
    :message: Someone just requested a password reset, please click this link to change your password immediately.
    """
    try:
        print("sent email", f"Your OTP is : {forgot_password_instance.otp}")

        # forgot_password_instance.is_sent = True
        # forgot_password_instance.save()
        # message = f"Dear {first_name}, <br><br>Welcome to Payarena Mall. <br>Please click <a href='{settings.FRONTEND_VERIFICATION_URL}/{profile.verification_code}/'>here</a> to verify your email."
        # subject = "Payarena Mall Email Verification"
        # contents = render(None, 'default_template.html', context={'message': message}).content.decode('utf-8')
        # send_email(content=, email=, subject=)
    except (Exception, ) as err:
        forgot_password_instance.is_sent = False
        forgot_password_instance.save()
        # Log
        print(err)
        return
