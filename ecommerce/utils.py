from django.db.models import Avg, Sum
from django.utils import timezone

from home.utils import get_week_start_and_end_datetime, get_month_start_and_end_datetime
from .models import Cart, Product, ProductDetail, CartProduct, ProductReview


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
    except (Exception, ) as err:
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


def top_weekly_products():
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
            {"id": product.id, "name": product.name, "image": product.image.get_image_url(), "rating": review,
             "price": product_detail.price, "discount": product_detail.discount, "featured": product.is_featured})
    return top_products


def top_monthly_categories():
    top_categories = []
    today_date = timezone.now()
    month_start, month_end = get_month_start_and_end_datetime(today_date)
    queryset = Product.objects.filter(
        created_on__gte=month_start, created_on__lte=month_end, status='active', store__is_active=True
    ).order_by("-sale_count").values("category__id", "category__name").annotate(Sum("sale_count")).order_by("-sale_count__sum")[:7]
    for product in queryset:
        category = dict()
        category['id'] = product['category__id']
        category['name'] = product['category__name']
        category['total_sold'] = product['sale_count__sum']
        top_categories.append(category)
    return top_categories
