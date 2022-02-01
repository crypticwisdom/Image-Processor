import datetime

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from .utils import create_account


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'detail': 'email and password is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=email, password=password)

        if not user:
            return Response({'detail': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

        user.last_login = datetime.datetime.now()
        user.save()

        return Response({
            'detail': 'login successful',
            'token': f"{RefreshToken.for_user(user).access_token}",
        })


class SignupView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'detail': 'email and password is required for signup'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'detail': 'user with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        success, response = create_account(request)
        ...
    




