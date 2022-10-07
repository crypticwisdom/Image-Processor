from django.shortcuts import render, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class HomeView(APIView):
    permission_classes = []

    def get(self, request):
        return HttpResponse('Welcome to PAYARENA MALL')



