import secrets
import uuid

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from ecommerce.shopper_email import shopper_welcome_email, shopper_signup_verification_email
from home.utils import log_request
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from .email import forgot_password_mail
from threading import Thread

from .serializers import ProfileSerializer
from .utils import validate_email, merge_carts, create_account, send_shopper_verification_email


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        try:
            email = request.data.get('email', None)
            password, user = request.data.get('password', None), None
            cart_uid = request.data.get("cart_uid", None)

            if email is None:
                return Response({"detail": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

            if password is None:
                return Response({"detail": "Password field is required"}, status=status.HTTP_400_BAD_REQUEST)

            if '@' in email:
                check = validate_email(email)
                if check is False:
                    return Response({"detail": "Email is not valid"}, status=status.HTTP_400_BAD_REQUEST)

                user = authenticate(request, username=email, password=password)

            log_request(f"user: {user}")

            if not user:
                return Response({"detail": "Incorrect user login details"}, status=status.HTTP_400_BAD_REQUEST)

            if Profile.objects.get(user=user).verified is False:
                return Response({"detail": "User not verified, please request a verification link."},
                                status=status.HTTP_400_BAD_REQUEST)

            merge_carts(cart_uid=cart_uid, user=user)

            return Response({
                "detail": "Login successful",
                "token": f"{RefreshToken.for_user(user).access_token}",
                "data": ProfileSerializer(Profile.objects.get(user=user), context={"request": request}).data
            })

        except (ValueError, Exception) as err:
            print(err)
            # Log error
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)


class SignupView(APIView):
    permission_classes = []

    def post(self, request):
        try:
            email = request.data.get("email", None)
            f_name, l_name = request.data.get("first_name", None), request.data.get("last_name", None)
            phone_number, password = request.data.get("phone_number", None), request.data.get("password", None)
            password_confirm = request.data.get("password_confirm", None)

            if not all([email, phone_number, password, password_confirm, f_name, l_name]):
                return Response({
                    "detail": "first name, last name, email, phone number, password, and "
                              "confirm password are required fields",
                }, status=status.HTTP_400_BAD_REQUEST)

            # if "@" in username:
            #     return Response({"detail": 'Character "@" is not allowed in username field'},
            #                     status=status.HTTP_400_BAD_REQUEST)

            # Check username exist
            if User.objects.filter(email=email).exists():
                return Response({"detail": "A user with this email already exists"},
                                status=status.HTTP_400_BAD_REQUEST)

            if validate_email(email) is False:
                return Response({"detail": "Invalid Email Format"}, status=status.HTTP_400_BAD_REQUEST)

            phone_number = f"+234{phone_number[-10:]}"

            if password != password_confirm:
                return Response({"detail": "Passwords mismatch"}, status=status.HTTP_400_BAD_REQUEST)

            success, profile_or_err_msg = create_account(email, phone_number, password, f_name, l_name)
            if success:
                # Send Verification code
                if send_shopper_verification_email(email=email, profile=profile_or_err_msg):
                    return Response({"detail": "Account created and Verification link has been sent Successfully"},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({"detail": "An error occurred while sending the verification link"},
                                    status=status.HTTP_400_BAD_REQUEST)

            return Response({"detail": profile_or_err_msg}, status=status.HTTP_400_BAD_REQUEST)

        except (Exception,) as err:
            print(err)
            # Log
            return Response({"detail": "An error occurred while creating this user"},
                            status=status.HTTP_400_BAD_REQUEST)


# Pending the flow for Forgot Password.
class ForgotPasswordSendOTPView(APIView):
    permission_classes = []

    def post(self, request):
        try:
            email = request.data.get("email")

            if email is None:
                return Response({"detail": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

            if '@' in email:
                if not validate_email(email):
                    return Response({"detail": "Invalid Email Format"}, status=status.HTTP_400_BAD_REQUEST)

                # Get user instance with email
                user_instance = User.objects.filter(email=email).first()
                if not user_instance:
                    return Response({"detail": "No user found with this email"}, status=status.HTTP_400_BAD_REQUEST)

                # email_or_username = user_instance.email
            # else:
            #     # Get user instance with username
            #     user_instance = User.objects.filter(username=email_or_username).first()
            #
            #     if not user_instance:
            #         return Response({"detail": "No user found with this username"}, status=status.HTTP_400_BAD_REQUEST)
            #
            #     email_or_username = user_instance.email

            # A forgot_password_instance is created to hold a generated_otp and the user's email.
            generated_otp = secrets.token_hex(3)
            forgot_password_instance = ForgotPasswordOTP(otp=generated_otp, email=email,
                                                         expire_time=timezone.now() + timezone.timedelta(minutes=5))
            forgot_password_instance.save()

            # Inform user that someone has requested a password reset with his email.
            # The notification would be sent with a link to redirect them to where they will enter a new password.

            # pass forgot_password_instance, into the 'forgot_password_mail' thread
            # run a cronjob to change the 'is_used' field to True after 5 minutes.
            Thread(target=forgot_password_mail, kwargs={"email": email,
                                                        "forgot_password_instance": forgot_password_instance}).start()

            return Response({"detail": "A message containing an OTP has been sent to your mail"},
                            status=status.HTTP_200_OK)
        except (TypeError, Exception) as err:
            print(err)
            # Log
            return Response({"detail": "An error occurred while receiving email for [password forgot]"},
                            status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            otp = request.data.get("otp", None)
            password, password_confirm = request.data.get("password", None), request.data.get("password_confirm", None)

            otp_instance = ForgotPasswordOTP.objects.get(otp=otp)
            if otp:
                if otp_instance.is_sent is False or timezone.now() > otp_instance.expire_time or otp_instance.is_used is True:
                    # Either mail was not sent or token has lived for 5 minutes (expired)
                    return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"detail": "OTP is field required"}, status=status.HTTP_400_BAD_REQUEST)

            if password is None:
                return Response({"detail": "Password is field required"}, status=status.HTTP_400_BAD_REQUEST)

            if password_confirm is None:
                return Response({"detail": "Password does not match"}, status=status.HTTP_400_BAD_REQUEST)

            if password != password_confirm:
                return Response({"detail": "Password does not match"}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.get(email=otp_instance.email)

            if user is not None:
                password = make_password(password=password)
                user.password = password
                user.save()

                otp_instance.is_used = True
                otp_instance.save()

                return Response({"detail": "Password reset successful"}, status=status.HTTP_200_OK)

            return Response({"detail": "Password reset was not successful"}, status=status.HTTP_400_BAD_REQUEST)
        except (Exception,) as err:
            print(err)
            # Log
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            old_password, new_password = request.data.get("old_password", None), request.data.get("new_password", None)
            confirm_new_password = request.data.get("confirm_new_password", None)

            if not all([old_password, new_password, confirm_new_password]):
                return Response({"detail": "All password fields are required"}, status=status.HTTP_400_BAD_REQUEST)

            if new_password != confirm_new_password:
                return Response({"detail": "Password does not match"}, status=status.HTTP_400_BAD_REQUEST)

            if not check_password(old_password, request.user.password):
                return Response({"detail": "Old password does not match your current password"},
                                status=status.HTTP_400_BAD_REQUEST)
            user = request.user
            user.password = make_password(confirm_new_password)
            user.save()

        except (Exception,) as err:
            print(err)
            # Log
        else:
            return Response({"detail": "Password has been changed"}, status=status.HTTP_201_CREATED)


class ResendVerificationLinkView(APIView):
    permission_classes = []

    def post(self, request):
        try:
            email = request.data.get("email", None)
            if not email:
                return Response({"detail": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

            profile = Profile.objects.get(user__email=email)

            if profile is not None:
                if send_shopper_verification_email(email=email, profile=profile):
                    return Response({"detail": "Verification link has been sent to the specified Email"},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({"detail": "An error occured while send verification link"},
                                    status=status.HTTP_400_BAD_REQUEST)

            return Response({"detail": "No Profile is linked to the Provided email"}, status=status.HTTP_400_BAD_REQUEST)
        except (Exception, ) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationLinkView(APIView):
    permission_classes = []

    def post(self, request, token=None):
        try:
            profile = Profile.objects.all().filter(verification_code=token)
            if not profile.exists():
                return Response({"detail": "Invalid Verification code"}, status=status.HTTP_400_BAD_REQUEST)

            profile = profile.last()

            # check if verification code is expired.
            print(timezone.now() <= profile.code_expiration_date, timezone.now(), profile.code_expiration_date)
            if timezone.now() >= profile.code_expiration_date:
                profile.verified = True
                # Empty the verification code
                profile.verification_code = ""
                profile.save()
                return Response({"detail": "Your Email has been verified successfully"}, status=status.HTTP_200_OK)

            profile.save()
            profile.verified = False
            profile.verification_code = ""
            profile.save()
            return Response({"detail": "Verification code has expired"},
                            status=status.HTTP_400_BAD_REQUEST)
        except (Exception, ) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)
