from rest_framework.permissions import BasePermission
from merchant.models import Seller


class IsMerchant(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        try:
            seller = Seller.objects.filter(user=request.user)
        except (Seller.DoesNotExist, ):
            return False
        else:
            # return False
            return bool(request.user and request.user.is_authenticated and seller is not None)

