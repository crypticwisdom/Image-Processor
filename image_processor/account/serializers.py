from rest_framework import serializers
from account.models import Client, ValidatorBlock


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'client_name', 'email']


class ValidationBlockSerializer(serializers.ModelSerializer):
    client_name = ClientSerializer(read_only=True, many=False)

    class Meta:
        model = ValidatorBlock
        exclude = ('created_on', 'updated_on')
