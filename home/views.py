from django.shortcuts import render, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from account.models import Profile
from merchant.utils import get_all_banks


class HomeView(APIView):
    permission_classes = []

    def get(self, request):
        return HttpResponse('Welcome to PAYARENA MALL')


class ListAllBanksAPIView(APIView):

    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        success, detail = get_all_banks(profile)
        if success is False:
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
        return Response(detail)

