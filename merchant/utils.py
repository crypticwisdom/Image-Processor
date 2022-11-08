import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Sum

from ecommerce.models import Product, ProductCategory, ProductType, ProductDetail, Brand, ProductImage, Image, \
    OrderProduct
from ecommerce.serializers import OrderProductSerializer
from home.utils import log_request, get_week_start_and_end_datetime, get_month_start_and_end_datetime, \
    get_year_start_and_end_datetime
from .models import *
from store.models import Store
from store.utils import create_or_update_store


def create_product(request, seller):
    data = request.data
    store = Store.objects.get(seller=seller)

    # Product Information
    name = data.get("name")
    image = data.get("image")
    cat_id = data.get("category_id")
    sub_cat_id = data.get("sub_category_id")
    prod_type_id = data.get("product_type_id")
    brand_id = data.get("brand_id")
    image_id = data.get('image_id', '')
    tag = data.get("tags", [])

    if not all([name, image, cat_id, sub_cat_id, prod_type_id, brand_id, image_id]):
        return False, "Name, image, category, sub category, brand, and product type are required fields", None

    category = ProductCategory.objects.get(id=cat_id)
    sub_category = ProductCategory.objects.get(id=sub_cat_id)
    prod_type = ProductType.objects.get(id=prod_type_id)
    brand = Brand.objects.get(id=brand_id)
    image = Image.objects.get(id=image_id)

    product, created = Product.objects.get_or_create(
        name=name, store=store, category=category, sub_category=sub_category, product_type=prod_type
    )
    product.brand = brand
    product.image = image
    product.save()
    if tag:
        tagging = ", ".join(tag)
        product.tags = tagging
        product.save()

    # Product Variants
    variant = data.get("variants", [])
    if variant:
        add_or_update_product_detail(variant, product)

    return True, "Product added successfully", product


def add_or_update_product_detail(variants, product):
    try:
        variation_list = list()
        for variation in variants:
            product_variation = None
            variation_id = variation.get('id', '')
            sku = variation.get('sku', '')
            size = variation.get('size', '')
            color = variation.get('color', '')
            discount = variation.get('discount', 0.0)
            price = variation.get('price', 0.0)
            stock = variation.get('stock', 0)
            images = variation.get('images', [])
            if variation_id:
                product_variation = ProductDetail.objects.get(pk=variation_id)
                product_variation.sku = sku
                product_variation.size = size
                product_variation.color = color
                product_variation.discount = discount
                product_variation.price = price
                product_variation.stock = stock
                product_variation.save()
            else:
                product_variation = ProductDetail.objects.create(
                    product=product, sku=sku, size=size, color=color, discount=discount, price=price, stock=stock
                )

            if product_variation.id not in variation_list:
                variation_list.append(product_variation.id)

            if product_variation:
                if images:
                    add_product_detail_images(images, product_variation)
        ProductDetail.objects.filter(product=product).exclude(id__in=variation_list).delete()

    except Exception as ex:
        log_request(f"An error occurred. Error: {ex}")


def add_product_detail_images(images, product_detail):
    try:
        ProductImage.objects.filter(product_detail=product_detail).delete()
        for image_obj in images:
            image_id = image_obj.get('id', '')
            image = Image.objects.get(pk=image_id)
            ProductImage.objects.create(product_detail=product_detail, image=image)
    except Exception as ex:
        log_request(f"An error occurred. Error: {ex}")


def update_product(request, product):
    data = request.data
    if 'name' in data:
        product.name = data.get('name', '')
    if 'status' in data:
        product.status = data.get('status', '')
    if 'category_id' in data:
        category_id = data.get('category_id', '')
        category = ProductCategory.objects.get(pk=category_id)
        product.category = category
    if 'sub_category_id' in data:
        sub_category_id = data.get('sub_category_id', '')
        sub_category = ProductCategory.objects.get(pk=sub_category_id)
        product.sub_category = sub_category
    if 'product_type_id' in data:
        product_type_id = data.get('product_type_id', '')
        product_type = ProductType.objects.get(pk=product_type_id)
        product.product_type = product_type
    if 'brand_id' in data:
        brand_id = data.get('brand_id', '')
        brand = Brand.objects.get(pk=brand_id)
        product.brand = brand
    if 'image_id' in data:
        image_id = data.get('image_id', '')
        image = Image.objects.get(pk=image_id)
        product.image = image
    if 'tags' in data:
        tags = data.get('tags', [])
        if tags:
            product.tags = ', '.join(tags)
    product.save()
    if 'variants' in data:
        variants = data.get('variants', [])
        add_or_update_product_detail(variants, product)

    return product


def create_seller(request, user, email, phone_number):
    store, seller, seller_detail, bank_account, = None, None, None, None
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
            return "Business town is required", False

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
                    direct = Director.objects.create(name=item['name'],
                                                     phone_number=f"+234{item['phone_number'][-10:]}")
                    seller_detail.director = direct
            seller_detail.save()

            bank_account = BankAccount.objects.create(
                seller=seller, bank_name=bank_name, account_name=bank_account_name,
                account_number=bank_account_number
            )
            return f"Created {company_name}", True

        else:
            return "Invalid Business Type", False
    except (Exception,) as err:
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


def get_total_sales(store):
    total_sales = 0
    total_sales_data = OrderProduct.objects.filter(product_detail__product__store=store, order__payment_status="success"
                                                   ).aggregate(total_sales=Sum('sub_total'))['total_sales']
    if total_sales_data:
        total_sales = total_sales_data
    return total_sales


def get_sales_data(store):
    sales = dict()
    weekly = []
    monthly = []
    yearly = []
    current_date = datetime.datetime.now()
    for delta in range(6, -1, -1):
        week_total_sales = 0
        month_total_sales = 0
        year_total_sales = 0
        week_date = current_date - relativedelta(weeks=delta)
        month_date = current_date - relativedelta(months=delta)
        year_date = current_date - relativedelta(years=delta)
        week_start, week_end = get_week_start_and_end_datetime(week_date)
        month_start, month_end = get_month_start_and_end_datetime(month_date)
        print(month_start, month_end)
        year_start, year_end = get_year_start_and_end_datetime(year_date)
        # print(year_start, year_end)
        total_sales = OrderProduct.objects.filter(product_detail__product__store=store, created_on__gte=week_start,
                                                  created_on__lte=week_end, order__payment_status="success"
                                                  ).aggregate(total_sales=Sum('sub_total'))['total_sales']
        if total_sales:
            week_total_sales = total_sales
        weekly.append({"week": week_start.strftime("%d %b"), "sales": week_total_sales})
        total_sales = OrderProduct.objects.filter(product_detail__product__store=store, created_on__gte=month_start,
                                                  created_on__lte=month_end, order__payment_status="success"
                                                  ).aggregate(total_sales=Sum('sub_total'))['total_sales']
        if total_sales:
            month_total_sales = total_sales
        monthly.append({"month": month_start.strftime("%b"), "sales": month_total_sales})
        total_sales = OrderProduct.objects.filter(product_detail__product__store=store, created_on__gte=year_start,
                                                  created_on__lte=year_end, order__payment_status="success"
                                                  ).aggregate(total_sales=Sum('sub_total'))['total_sales']
        if total_sales:
            year_total_sales = total_sales
        yearly.append({"year": year_start.strftime("%Y"), "sales": year_total_sales})
    sales['weekly'] = weekly
    sales['monthly'] = monthly
    sales['yearly'] = yearly
    return sales


def get_best_sellers_data(store):
    best_sellers = []
    query_set = OrderProduct.objects.filter(product_detail__product__store=store, order__payment_status="success"
                                            ).values('product_detail__id').annotate(Sum('quantity')).order_by(
        '-quantity__sum')[:4]
    for data in query_set:
        product = dict()
        product_variant = ProductDetail.objects.get(pk=data['product_detail__id'])
        product['id'] = product_variant.product.id
        product['sku'] = product_variant.sku
        product['name'] = product_variant.product.name
        product['image'] = product_variant.product.image.image.url
        product['price'] = product_variant.price
        product['units'] = data['quantity__sum']
        best_sellers.append(product)
    return best_sellers


def get_top_categories_data(store):
    top_categories = []
    query_set = OrderProduct.objects.filter(product_detail__product__store=store, order__payment_status="success"
                                            ).values(
        'product_detail__product__category__id',
        'product_detail__product__category__name').annotate(
        Sum('quantity')).order_by('-quantity__sum')[:6]
    for order_product in query_set:
        category = dict()
        category['id'] = order_product['product_detail__product__category__id']
        category['name'] = order_product['product_detail__product__category__name']
        category['units'] = order_product['quantity__sum']
        top_categories.append(category)
    return top_categories


def get_recent_orders_data(store):
    serializer = OrderProductSerializer(
        OrderProduct.objects.filter(product_detail__product__store=store, order__payment_status="success"
                                    ).order_by('-created_on')[:10],
        many=True)
    return serializer.data


def get_dashboard_data(store):
    data = dict()
    data['total_orders'] = OrderProduct.objects.filter(product_detail__product__store=store,
                                                       order__payment_status="success").count()
    data['total_sales'] = get_total_sales(store)
    data['product_views'] = Product.objects.filter(store=store).aggregate(Sum('view_count'))['view_count__sum']
    data['sales'] = get_sales_data(store)
    data['best_sellers'] = get_best_sellers_data(store)
    data['top_categories'] = get_top_categories_data(store)
    data['recent_orders'] = get_recent_orders_data(store)
    return data

