import base64
import datetime
import decimal

from cryptography.fernet import Fernet
from django.conf import settings
from django.db import transaction
from django.db.models import Avg, Sum
from django.utils import timezone

from account.models import Address
from home.utils import get_week_start_and_end_datetime, get_month_start_and_end_datetime, get_next_date
from module.shipping_service import ShippingService
from .models import Cart, Product, ProductDetail, CartProduct, ProductReview, Order, OrderProduct


def sorted_queryset(order_by, query):
    queryset = Product.objects.filter(query).order_by('-updated_on').distinct()
    if order_by == 'highest_price':
        queryset = Product.objects.filter(query).order_by('-productdetail__price').distinct()
    if order_by == 'lowest_price':
        queryset = Product.objects.filter(query).order_by('productdetail__price').distinct()
    if order_by == 'highest_discount':
        queryset = Product.objects.filter(query).order_by('-productdetail__discount').distinct()
    if order_by == 'lowest_discount':
        queryset = Product.objects.filter(query).order_by('productdetail__discount').distinct()
    if order_by == 'highest_rating':
        queryset = Product.objects.filter(query).order_by('-productreview__rating').distinct()
    if order_by == 'lowest_rating':
        queryset = Product.objects.filter(query).order_by('productreview__rating').distinct()
    return queryset


def check_cart(user=None, cart_id=None, cart_uid=None):
    if cart_uid is not None:
        cart_check = Cart.objects.filter(cart_uid=cart_uid, status="open").exists()
        return cart_check, Cart.objects.filter(cart_uid=cart_uid, status="open")

    if cart_id is not None:
        return Cart.objects.filter(id=cart_id, status="open").exists(), Cart.objects.filter(id=cart_id, status="open")

    if Cart.objects.filter(user=user, status="open").exists():
        return True, Cart.objects.filter(user=user, status="open")

    return False, "Cart not found"


def create_cart_product(product_id, cart):
    try:
        # Get product detail with the 'product_id'
        if ProductDetail.objects.filter(product__id=product_id).exists():
            product_detail = ProductDetail.objects.get(product__id=product_id)

            # Create Cart Product
            cart_product = CartProduct.objects.create(
                cart=cart, product_detail=product_detail, price=product_detail.price,
                discount=product_detail.discount, quantity=1)
            return True, cart_product
        return False, "Something went wrong while creating cart product"
    except (Exception,) as err:
        return False, f"{err}"


def perform_operation(operation_param, product_detail, cart_product):
    # what operation to perform ?
    if operation_param not in ("+", "-", "remove"):
        print("Invalid operation parameter expecting -, +, remove")
        return False, "Invalid operation parameter expecting -, +, remove"

    if operation_param == "+":
        if product_detail.stock > cart_product.quantity + 1:
            cart_product.quantity += 1
            cart_product.price += product_detail.price
            cart_product.save()
            return True, "Added product to cart"
        else:
            # product is out of stock
            return False, "Product is out of stock"

    if operation_param == "-":
        if cart_product.quantity == 1:
            # remove from cart and give response.
            cart_product.delete()
            return True, "Cart product has been removed"

        if cart_product.quantity > 1:
            #   reduce prod_cart and give responses.
            cart_product.quantity -= 1
            cart_product.price -= product_detail.price
            cart_product.save()
            return True, "Cart product has been reduced"

        # Product not available
        return False, "Product is not in cart"

    if operation_param == "remove":
        # remove product and give response
        cart_product.delete()
        return True, "Cart product has been removed"


def top_weekly_products(request):
    top_products = []
    current_date = timezone.now()
    week_start, week_end = get_week_start_and_end_datetime(current_date)
    query_set = Product.objects.filter(
        created_on__gte=week_start, created_on__lte=week_end, status='active', store__is_active=True).order_by(
        "-sale_count"
    )[:20]
    for product in query_set:
        review = ProductReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg'] or 0
        product_detail = ProductDetail.objects.filter(product=product).last()
        top_products.append(
            {"id": product.id, "name": product.name, "image": request.build_absolute_uri(product.image.image.url),
             "rating": review,
             "price": product_detail.price, "discount": product_detail.discount, "featured": product.is_featured})
    return top_products


def top_monthly_categories():
    top_categories = []
    today_date = timezone.now()
    month_start, month_end = get_month_start_and_end_datetime(today_date)
    queryset = Product.objects.filter(
        created_on__gte=month_start, created_on__lte=month_end, status='active', store__is_active=True
    ).order_by("-sale_count").values("category__id", "category__name").annotate(Sum("sale_count")).order_by(
        "-sale_count__sum")[:7]
    for product in queryset:
        category = dict()
        category['id'] = product['category__id']
        category['name'] = product['category__name']
        category['total_sold'] = product['sale_count__sum']
        top_categories.append(category)
    return top_categories


def validate_product_in_cart(customer):
    response = list()
    cart = Cart.objects.get(user=customer.user, status="open")
    cart_products = CartProduct.objects.filter(cart=cart)
    for product in cart_products:
        product_detail = product.product_detail
        if product_detail.product.status != "active" or product_detail.product.store.is_active is False:
            response.append({"product_name": f"{product_detail.product.name}",
                             "detail": "Product is not available for delivery at the moment"})

        if product_detail.stock == 0:
            response.append({"product_name": f"{product_detail.product.name}",
                             "detail": "Product is out of stock"})

        if product.quantity > product_detail.stock:
            response.append(
                {"product_name": f"{product_detail.product.name}",
                 "detail": f"Requested quantity is more than the available in stock: {product_detail.stock}"}
            )

    return response


def get_shipping_rate(customer, address_id=None):
    # response = dict()
    shippers_list = list()
    sellers_products = list()

    if Address.objects.filter(id=address_id, customer=customer).exists():
        address = Address.objects.get(id=address_id, customer=customer)
    elif Address.objects.filter(customer=customer, is_primary=True).exists():
        address = Address.objects.get(customer=customer, is_primary=True)
    else:
        address = Address.objects.filter(customer=customer).first()

    cart = Cart.objects.get(user=customer.user, status="open")

    # Get products in cart
    cart_products = CartProduct.objects.filter(cart=cart)

    # Get each seller in cart
    # sellers_in_cart = list()
    # for product in cart_products:
    #     seller = product.product_detail.product.store.seller
    #     sellers_in_cart.append(seller)

    for product in cart_products:
        products_for_seller = {
            'seller': product.product_detail.product.store.seller,
            'seller_id': product.product_detail.product.store.seller_id,
            'products': [
                {
                    'cart_product_id': product.id,
                    'quantity': product.quantity,
                    'weight': product.product_detail.weight,
                    'price': product.product_detail.price,
                    'product': product.product_detail.product,
                    'detail': product.product_detail.description,
                }
            ],
        }
        if products_for_seller not in sellers_products:
            sellers_products.append(products_for_seller)

    # Get products belonging to each seller
    # for seller in sellers_in_cart:
    #     products_for_seller = {
    #         'seller': seller,
    #         'seller_id': seller.id,
    #         'products': [
    #             {
    #                 'cart_product_id': cart_product.id,
    #                 'quantity': cart_product.quantity,
    #                 'weight': cart_product.product_detail.weight,
    #                 'price': cart_product.product_detail.price,
    #                 'product': cart_product.product_detail.product,
    #                 'detail': cart_product.product_detail.description,
    #             }
    #             for cart_product in cart_products.distinct()
    #             if cart_product.product_detail.product.store.seller == seller
    #         ],
    #     }
    #     if products_for_seller not in sellers_products:
    #         sellers_products.append(products_for_seller)

    # Call shipping API
    rating = ShippingService.rating(
        sellers=sellers_products, customer=customer, customer_address=address
    )

    for rate in rating:
        shipper = dict()
        shipper["name"] = rate["ShipperName"]
        detail_list = list()
        quote_list = rate["QuoteList"]
        for item in quote_list:
            detail = dict()
            detail["cart_product_id"] = item["Id"]
            detail["company_id"] = item["CompanyID"]
            detail["shipping_fee"] = item["Total"]
            detail_list.append(detail)
        # shipper["shipping_fee"] = decimal.Decimal(rate["TotalPrice"])
        shipper["shipping_information"] = detail_list
        shippers_list.append(shipper)

    # sub_total = cart_products.aggregate(Sum("price"))["price__sum"] or 0
    # response["sub_total"] = sub_total
    # response["shippers"] = shippers_list
    return shippers_list


def order_payment(payment_method, order):
    # if payment_method == "success":
    # create Transaction
    # create cart_bill
    # update order_payment
    order.payment_status = "success"
    order.save()

    return True, "Payment successful"


def add_order_product(order):
    cart_product = CartProduct.objects.filter(cart__order=order)
    for product in cart_product:
        total = product.price - product.discount
        three_days_time = get_next_date(timezone.datetime.now(), 3)
        # Create order product instance for items in cart
        order_product, _ = OrderProduct.objects.get_or_create(order=order, product_detail=product.product_detail)
        order_product.price = product.price
        order_product.quantity = product.quantity
        order_product.discount = product.discount
        order_product.total = total
        order_product.delivery_date = three_days_time
        order_product.payment_on = timezone.datetime.now()
        order_product.shipper_name = product.shipper_name
        order_product.company_id = product.company_id
        order_product.delivery_fee = product.delivery_fee
        order_product.save()

        # Increase sale count
        order_product.product_detail.product.sale_count += order_product.quantity
        order_product.product_detail.product.save()
        # Reduce Item stock
        order_product.product_detail.stock -= order_product.quantity
        order_product.product_detail.save()

    # Discard the cart
    order.cart.status = "closed"
    order.cart.save()

    order_products = OrderProduct.objects.filter(order=order)

    return order_products


def check_product_stock_level(product):
    # This function is to be called when an Item is packed or reduced from the stock
    product_detail = ProductDetail.objects.get(product=product)
    if product_detail.stock <= product_detail.low_stock_threshold:
        product_detail.out_of_stock_date = timezone.datetime.now()
        product_detail.save()
        # Send email to merchant
    return True


def perform_order_cancellation(order, user):
    order_products = OrderProduct.objects.filter(order=order)
    for order_product in order_products:
        if order_product.status != "paid":
            return False, "This order has been processed, and cannot be cancelled"
    order_products.update(status="cancelled", cancelled_on=timezone.datetime.now(), cancelled_by=user)
    return True, "Order cancelled successfully"


def perform_order_pickup(order_product, address, sender_town_id, receiver_town_id):
    summary = f"Shipment Request to {address.get_full_address()}"
    response = ShippingService.pickup(
        order_products=order_product, address=address, order_summary=summary, sender_town_id=sender_town_id,
        receiver_town_id=receiver_town_id
    )

    if "error" in response:
        return False, "Order cannot be placed at the moment"

    # Update OrderProduct
    for data in response:
        shipper = str(data["Shipper"]).upper()
        order_no = data["OrderNo"]
        delivery_fee = data["TotalAmount"]
        waybill = data["TrackingNo"]

        order_product.filter(shipper_name=shipper).update(
            tracking_id=order_no, delivery_fee=delivery_fee, waybill_no=waybill, status="packed",
            packed_on=datetime.datetime.now()
        )

    return True, "Pickup request was successful"


def perform_order_tracking(order_product):
    tracking_id = order_product.tracking_id
    response = ShippingService.track_order(tracking_id)

    if "error" in response:
        return False, "An error occurred while tracking order. Please try again later"

    detail = list()
    for item in response:
        data = dict()
        data["status"] = item["Status"]
        detail.append(data)

    return True, detail


def encrypt_text(text: str):
    key = base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32])
    fernet = Fernet(key)
    secure = fernet.encrypt(f"{text}".encode())
    return secure.decode()


def decrypt_text(text: str):
    key = base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32])
    fernet = Fernet(key)
    decrypt = fernet.decrypt(text.encode())
    return decrypt.decode()



