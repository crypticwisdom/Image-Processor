from django.shortcuts import render
from .serializers import SellerSerializer
from .models import Seller, SellerVerification, SellerFile
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth import authenticate
from rest_framework import serializers

from rest_framework.authtoken.models import Token

# Create your views here.


class SellerViews(APIView):
    item = Seller.objects.filter()
    serializer = SellerSerializer()
    permission_classes = [IsAuthenticated]


    def get(self, request, id=None):
        if id:
            item = Seller.objects.filter(id=id)
            serializer = SellerSerializer(item)
            return Response({"status": True, "data": serializer.data}, status=status.HTTP_200_OK)

        item = Seller.objects.all()
        serializer = SellerSerializer(item, many=True)
        return Response({"status": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        phone = request.data.get('phone', '')
        cac = request.data.get('cac_number', '')
        id_card = request.data.get('id_card',)
        file = request.data.get('file', '')

        seller = Seller.objects.get(user=request.user)

        # seller = Seller.objects.create(phone_number=phone)
        print(seller)
        # seller.save()

        sellerVerification = SellerVerification.objects.create(seller=seller, cac_number=cac, id_card=id_card)
        sellerVerification.save()

        return Response({"status": "success", "data": sellerVerification}, status=status.HTTP_400_BAD_REQUEST)
        # serializer = SellerSerializer(phone)

        # if serializer.is_valid():
        #     serializer.save()
        #     return Response({"status":"success", "data":serializer.data}, status=status.HTTP_200_OK)
        #
        # else:
        #     return Response({"status":"error", "data":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SignInSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        # data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        new_data = {"token" : data['access']}

        return new_data


class SignIn(TokenObtainPairView):
    serializer_class = SignInSerializer
