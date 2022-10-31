from ecommerce.models import ProductCategory
from .models import *
from store.models import Store
from store.utils import create_or_update_store
from rest_framework.response import Response
from rest_framework import status


def create_update_seller(seller, request):
    seller.phone_number = request.data.get('phone')
    seller.address = request.data.get('address')
    seller.city_id = request.data.get('city_id')
    seller.state_id = request.data.get('state_id')
    seller.country_id = request.data.get('country_id')
    seller.status = request.data.get('status')
    seller.save()

    verification, created = SellerDetail.objects.get_or_create(seller=seller)
    verification.cac_number = request.data.get('cac_number')
    verification.save()

    store, created = Store.objects.get_or_create(seller=seller)
    create_or_update_store(store, request)

    return True


def create_seller(request, user, email):
    first_name = request.data.get('first_name', None)
    if not first_name:
        return "First name is required", False

    last_name = request.data.get('last_name', None)
    if not last_name:
        return "Last name is required", False

    phone_number = request.data.get('phone_number', None)
    if phone_number is not None and str(phone_number[-10:]).isnumeric():
        phone_number = f"{+234} {phone_number[-10:]}"
    else:
        return "Phone Number is required", False

    business_name = request.data.get("business_name", None)
    if not business_name:
        return "Business name is required", False

    product_category = request.data.get("product_category", [])  # drop-down
    if not product_category:
        return "Product category is required", False

    business_address = request.data.get("business_address", None)
    if not business_address:
        return "Business address is required", False

    business_town = request.data.get("business_town", None)
    if not business_town:
        return Response({"detail": "Business town is required"}, status=status.HTTP_400_BAD_REQUEST)

    business_state = request.data.get("business_state", None)  # drop-down
    if not business_state:
        return "Business State is required", False

    business_city = request.data.get("business_city", None)  # drop-down
    if not business_city:
        return "Business City is required", False

    latitude = request.data.get("latitude", None)  # drop-down
    if not latitude:
        return "Latitude is required", False

    longitude = request.data.get("longitude", None)  # drop-down
    if not longitude:
        return "Longitude is required", False

    business_drop_off_address = request.data.get("business_drop_off_address", None)
    if not business_drop_off_address:
        return "Business drop off address is required", False

    business_type = request.data.get("business_type", None)
    if not business_type:
        return "Business type is required", False

    # ----------------------------------------------------------------------------

    directors = request.data.get("directors", [])
    market_size = request.data.get("market_size", None)
    number_of_outlets = request.data.get("number_of_outlet", None)
    maximum_price_range = request.data.get("maximum_price_range", None)  # drop-down
    bank_account_number = request.data.get("bank_account_number", None)
    bank_name = request.data.get("bank_name", None)  # drop-down
    bank_account_name = request.data.get("bank_account_name", None)

    if not str(bank_account_number).isnumeric():
        if len(bank_account_number) == 10:
            return "Invalid account number format", False

    # -------------------------------------------------------------------------------------
    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.save()

    if business_type == "unregistered-individual-business":
        seller = Seller.objects.create(
            user=user, phone_number=phone_number, address=business_address,
            town=business_town, city=business_city, state=business_state,
            longitude=longitude, latitude=latitude
        )
        if seller is not None:
            # Create a store instance

            store = Store.objects.create(seller=seller, name=business_name)
            seller_detail = SellerDetail.objects.create(
                seller=seller,
                market_size=market_size,
                business_type=business_type,
                number_of_outlets=number_of_outlets,
                maximum_price_range=maximum_price_range
            )

            bank_account = BankAccount.objects.create(
                seller=seller, bank_name=bank_name, account_name=bank_account_name,
                account_number=bank_account_number
            )

            # features = request.data.get("features", [])  # list of M2M id's # Copied from Ashavin
            if product_category:
                store.categories.clear()
                for item in product_category:
                    try:
                        product_category = ProductCategory.objects.get(id=item)
                        store.categories.add(product_category)
                    except Exception as ex:
                        print(ex)

        # send email notification
        return f"Created {business_name}", True
    elif business_type == "registered-individual-business":
        company_name = ""
        company_type = ""
        cac_number = ''
        company_tin_number = ''
        market_size = ''
        number_of_outlets = ''
        max_price_range = ''
        bank_acct_number = ''
        select_bank = ''
        bank_acct_no = ''

    elif business_type == "limited-liability-company":
        company_name = ''
        cac_no = ''
        company_tin = ''
        market_size = ''
        number_of_outlets = ''
        maximum_price_range = ''
        directors = ''
        director_name = ''
        director_number = ''

    else:
        ...



