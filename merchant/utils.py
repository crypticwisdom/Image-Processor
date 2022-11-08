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


def create_seller(request, user, email, phone_number):
    store, seller, seller_detail, bank_account,  = None, None, None, None
    try:

        first_name: str = request.data.get('first_name', None)
        if not first_name:
            return "First name is required", False

        last_name: str = request.data.get('last_name', None)
        if not last_name:
            return "Last name is required", False

        business_name: str = request.data.get("business_name", None)
        if not business_name:
            return "Business name is required", False

        product_category: list = request.data.get("product_category", [])  # drop-down
        if not product_category:
            return "Product category is required", False

        business_address: str = request.data.get("business_address", None)
        if not business_address:
            return "Business address is required", False

        business_town: str = request.data.get("business_town", None)
        if not business_town:
            return Response({"detail": "Business town is required"}, status=status.HTTP_400_BAD_REQUEST)

        business_state: str = request.data.get("business_state", None)  # drop-down
        if not business_state:
            return "Business State is required", False

        business_city: str = request.data.get("business_city", None)  # drop-down
        if not business_city:
            return "Business City is required", False

        latitude: float = request.data.get("latitude", None)  # drop-down
        if not latitude:
            return "Latitude is required", False

        longitude: float = request.data.get("longitude", None)  # drop-down
        if not longitude:
            return "Longitude is required", False

        business_drop_off_address: str = request.data.get("business_drop_off_address", None)
        if not business_drop_off_address:
            return "Business drop off address is required", False

        business_type: str = request.data.get("business_type", None)
        if not business_type:
            return "Business type is required", False

        bank_account_number: str = request.data.get("bank_account_number", None)
        if not bank_account_number:
            return "Bank account number is required", False

        bank_name: str = request.data.get("bank_name", None)  # drop-down
        if not bank_name:
            return "Bank name is required", False

        bank_account_name: str = request.data.get("bank_account_name", None)
        if not bank_account_name:
            return "Bank account name is required", False

        # ----------------------------------------------------------------------------

        # directors = request.data.get("directors", [])
        market_size: int = request.data.get("market_size", None)
        number_of_outlets: int = request.data.get("number_of_outlets", None)
        maximum_price_range: float = request.data.get("maximum_price_range", None)  # drop-down

        if not str(bank_account_number).isnumeric():
            if len(bank_account_number) == 10:
                return "Invalid account number format", False

        # -------------------------------------------------------------------------------------
        user.first_name = first_name.capitalize()
        user.last_name = last_name.capitalize()
        user.email = email
        user.save()

        seller = Seller.objects.create(
            user=user, phone_number=phone_number, address=business_address,
            town=business_town, city=business_city, state=business_state,
            longitude=longitude, latitude=latitude
        )
        if business_type == "unregistered-individual-business":

            if seller is not None:
                # Create a store instance

                store = Store.objects.create(seller=seller, name=business_name.capitalize())
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
                        product_category = ProductCategory.objects.get(id=item)
                        store.categories.add(product_category)

            # send email notification
            return f"Created {business_name}", True
        elif business_type == "registered-individual-business":

            company_name: str = request.data.get("company_name", None)
            company_type: str = request.data.get("company_type", None)
            cac_number = request.data.get("cac_number", None)
            company_tin_number = request.data.get("company_tin_number", None)
            market_size = request.data.get("market_size", None)
            number_of_outlets = request.data.get("number_of_outlets", None)
            maximum_price_range = request.data.get("maximum_price_range", None)  # drop-down

            if not company_name:
                return "Company name is required", False

            if company_type not in ['sole-proprietorship', 'partnership']:
                return "Company type is required", False

            if not cac_number:
                return "CAC Number is required", False

            if not company_tin_number:
                return "Company TIN number is required", False

            if not market_size:
                return "Market size is required", False

            if not number_of_outlets:
                return "Number of outlet is required", False

            if not maximum_price_range:
                return "Maximum price range is required", False

            if seller is not None:
                # Create a store instance

                store = Store.objects.create(seller=seller, name=business_name.capitalize())

                seller_detail = SellerDetail.objects.create(
                    seller=seller,
                    company_name=company_name.capitalize(),
                    company_type=company_type,
                    market_size=market_size,
                    business_type=business_type,
                    cac_number=cac_number,
                    company_tin_number=company_tin_number,
                    number_of_outlets=number_of_outlets,
                    maximum_price_range=maximum_price_range
                )

                bank_account = BankAccount.objects.create(
                    seller=seller, bank_name=bank_name, account_name=bank_account_name,
                    account_number=bank_account_number
                )

            # send email notification
            return f"Created {business_name}", True
        elif business_type == "limited-liability-company":

            company_name = request.data.get("company_name", None)
            # company_type = request.data.get("company_type", None)
            cac_number = request.data.get("cac_number", None)
            company_tin_number = request.data.get("company_tin_number", None)
            market_size = request.data.get("market_size", None)
            number_of_outlets = request.data.get("number_of_outlets", None)
            maximum_price_range = request.data.get("maximum_price_range", None)  # drop-down
            directors = request.data.get("directors", [])

            if not company_name:
                return "Company name is required", False

            # if company_type not in ['sole-proprietorship', 'partnership']:
            #     return "Company type is required", False
            company_type = "partnership"

            if not cac_number:
                return "CAC Number is required", False

            if not company_tin_number:
                return "Company TIN number is required", False

            if not market_size:
                return "Market size is required", False

            if not number_of_outlets:
                return "Number of outlet is required", False

            if not maximum_price_range:
                return "Maximum price range is required", False

            if not directors:
                return "Please input your partner's name and number.", False

            store = Store.objects.create(seller=seller, name=business_name.capitalize())

            # directors // expect a dictionary --> [
            #          ->                             {
            #                                               'name': 'Nwachukwu Wisdom',
            #          ->                                   'phone number': 08057784796
            #                                           }
            #          ->                          ]

            seller_detail = SellerDetail.objects.create(
                seller=seller,
                company_name=company_name,
                company_type=company_type,
                market_size=market_size,
                business_type=business_type,
                cac_number=cac_number,
                company_tin_number=company_tin_number,
                number_of_outlets=number_of_outlets,
                maximum_price_range=maximum_price_range
            )

            for item in directors:
                if item['name'] and item['phone_number'] and ['address']:
                    direct = Director.objects.create(name=item['name'], phone_number=f"+234{item['phone_number'][-10:]}")
                    seller_detail.director = direct
            seller_detail.save()

            bank_account = BankAccount.objects.create(
                seller=seller, bank_name=bank_name, account_name=bank_account_name,
                account_number=bank_account_number
            )
            return f"Created {company_name}", True

        else:
            return "Invalid Business Type", False
    except (Exception, ) as err:
        # store, seller, seller_detail, bank_account
        message = None
        # Delete 'store' instance when an 'Error' occur.
        if store is not None:
            store.delete()

        # Delete 'seller' instance when an 'Error' occur.
        if seller is not None:
            seller.delete()

        # Delete 'seller_detail' instance when an 'Error' occur.
        if seller_detail is not None:
            seller_detail.delete()

        # Delete 'bank_account' instance when an 'Error' occur.
        if bank_account is not None:
            bank_account.delete()

        # Check: if this user is not an authenticated user trying to register.
        # User instance will be created for this type of 'user' but he would need to login to complete registration
        if request.user.is_authenticated is False and user is not None:
            return "improper merchant creation", True

        return f"{err}.", False


