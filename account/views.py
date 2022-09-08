import datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from account import utils
from django.utils.timezone import now
from .email import forgot_password_mail
from threading import Thread


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        try:
            email = request.data.get('email', None)
            password = request.data.get('password', None)

            if not email or not password:
                return Response({'detail': 'email and password are required field'}, status=status.HTTP_400_BAD_REQUEST)
            print(request.user)
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user=user)
                user.last_login = now()
                user.save()

                if request.user.is_authenticated:
                    return Response({'detail': 'Login successful', 'token': f"{RefreshToken.for_user(user).access_token}"},
                                    status=status.HTTP_200_OK)

            return Response({'detail': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)
        except (Exception, ) as err:
            print(err)
            # Log
            return Response({'detail': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)


class SignupView(APIView):
    permission_classes = []

    def post(self, request):
        try:
            username, email = request.data.get("username", None), request.data.get("email", None)
            phone_number, password = request.data.get("phone_number", None), request.data.get("password", None)
            password_confirm = request.data.get("password_confirm", None)

            if username is None:
                return Response({"detail": "Username field is required"}, status=status.HTTP_400_BAD_REQUEST)

            if email is None:
                return Response({"detail": "Email field is required"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if utils.validate_email(email) is False:
                    return Response({"detail": "Invalid Email Format"}, status=status.HTTP_400_BAD_REQUEST)
                email = email

            if phone_number is None:
                return Response({"detail": "Phone Number field is required"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                phone_number = f"+234{phone_number[-10:]}"

            if password_confirm is None:
                return Response({"detail": "Confirm password field is required"}, status=status.HTTP_400_BAD_REQUEST)

            if password != password_confirm:
                return Response({"detail": "Password does not match"}, status=status.HTTP_400_BAD_REQUEST)

            success, msg = utils.create_account(username, email, phone_number, password)
            if success:
                return Response({"detail": "User has been created"}, status=status.HTTP_201_CREATED)
            return Response({"detail": msg}, status=status.HTTP_400_BAD_REQUEST)

        except (Exception, ) as err:
            print(err)
            # Log
            return Response({"detail": "An error occurred while creating this user"}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            email_or_username, email, username = request.data.get("email_or_username"), None, None

            if email_or_username is None:
                return Response({"detail": "Email or Username is required"}, status=status.HTTP_400_BAD_REQUEST)
            print(email_or_username)

            if '@' in email_or_username:
                if not utils.validate_email(email_or_username):
                    return Response({"detail": "Invalid Email Format"}, status=status.HTTP_400_BAD_REQUEST)

                # Get user instance with email
                user_instance = User.objects.filter(email=email_or_username).first()
                if not user_instance:
                    return Response({"detail": "No user found with this email"}, status=status.HTTP_400_BAD_REQUEST)

                email_or_username = user_instance.email

            else:
                # Get user instance with username
                user_instance = User.objects.filter(username=email_or_username).first()

                if not user_instance:
                    return Response({"detail": "No user found with this username"}, status=status.HTTP_400_BAD_REQUEST)
                email_or_username = user_instance.email

            # Inform user that someone has requested a password reset with his email.
            # The notification would be sent with a link to redirect them to where they will enter a new password.

            Thread(target=forgot_password_mail, args=[email_or_username]).start()

            return Response({"detail": "Email has been sent"}, status=status.HTTP_200_OK)
        except (TypeError, Exception) as err:
            print(err)
            # Log
            return Response({"detail": "An error occurred while receiving email for [password forgot]"},
                            status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            password, password_confirm = request.data.get("password", None), request.data.get("password_confirm", None)
            email = request.data.get("email", "")
            if password is None:
                return Response({"detail": "Password is field required"}, status=status.HTTP_400_BAD_REQUEST)

            if password_confirm is None:
                return Response({"detail": "Password does not match"}, status=status.HTTP_400_BAD_REQUEST)

            if password != password_confirm:
                return Response({"detail": "Password does not match"}, status=status.HTTP_400_BAD_REQUEST)

            # if
        except (Exception, ) as err:
            print(err)
            # Log
            return Response({"detail": ""}, status=status.HTTP_400_BAD_REQUEST)
