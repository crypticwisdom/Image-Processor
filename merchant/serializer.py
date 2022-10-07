from rest_framework.serializers import ModelSerializer
from merchant.models import Seller


class SellerSerializer(ModelSerializer):
    class Meta:
        model = Seller
        exclude = ()
