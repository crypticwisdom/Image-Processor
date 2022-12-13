from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from account.models import Profile
from merchant.utils import get_all_banks

from django.conf import settings
frontend_base_url = settings.FRONTEND_URL


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


class PaymentVerifyAPIView(APIView):
    permission_classes = []

    def post(self, request):
        expected_data = {
            "amount": "20.00",
            "description": "Funds for Dstv^WEBID38627",
            "fee": "0.00",
            "currency": "566",
            "status": "DECLINED",
            "scheme": "VISA",
            "transactionDateTime": "12/13/2022 11:03:17 AM",
            "statusDescription": "EXPIRED"
        }
        from home.utils import log_request
        log_request(request.data)
        return HttpResponseRedirect(redirect_to=f"{frontend_base_url}/verify-checkout?status={status}")


