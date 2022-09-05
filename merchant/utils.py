from .models import *
from store.models import Store
from store.utils import create_or_update_store


def create_update_seller(seller, request):
    seller.phone_number = request.data.get('phone')
    seller.address = request.data.get('address')
    seller.city_id = request.data.get('city_id')
    seller.state_id = request.data.get('state_id')
    seller.country_id = request.data.get('country_id')
    seller.status = request.data.get('status')
    seller.save()

    verification, created = SellerVerification.objects.get_or_create(seller=seller)
    verification.cac_number = request.data.get('cac_number')
    verification.save()

    store, created = Store.objects.get_or_create(seller=seller)
    create_or_update_store(store, request)

    return True



