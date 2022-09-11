def forgot_password_mail(*, email, forgot_password_instance):
    """
    :param forgot_password_instance:
    :param email:
    :return: None:
    :message: Someone just requested a password reset, please click this link to change your password immediately.
    """
    try:
        print("sent email", f"Your OTP is : {forgot_password_instance.otp}")

        forgot_password_instance.is_sent = True
        forgot_password_instance.save()
    except (Exception, ) as err:
        forgot_password_instance.is_sent = False
        forgot_password_instance.save()
        # Log
        print(err)
        return
