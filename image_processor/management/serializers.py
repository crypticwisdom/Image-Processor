from .models import ApplicationContentType, ApplicationExtension
from rest_framework import serializers


class ApplicationContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationContentType
        fields = "__all__"


class ApplicationExtensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationExtension
        fields = "__all__"
