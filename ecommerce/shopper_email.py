from django.contrib.auth.models import User
from django.shortcuts import render

from module.email_service import send_email
from django.conf import settings


def shopper_signup_verification_email(email, profile):
    first_name = profile.user.first_name
    if not profile.user.first_name:
        first_name = "Payarena Shopper"

    message = f"Dear {first_name}, <br><br>Welcome to Payarena Mall. <br>Please click <a href='{settings.FRONTEND_VERIFICATION_URL}/{profile.verification_code}/'>here</a> to verify your email."
    subject = "Payarena Mall Email Verification"
    contents = render(None, 'default_template.html', context={'message': message}).content.decode('utf-8')
    send_email(contents, email, subject)
    return True


def shopper_welcome_email(email):
    first_name = User.objects.get(email=email).first_name
    frontend_link = settings.FRONTEND_URL

    if not first_name:
        first_name = "Payarena Shopper"

    message = f'<p class="letter-heading">Hello There, <span>{first_name}!</span> <br><br><br><br></p>' \
              f'<div class="letter-body"><p>Welcome to Payarena Mall.<br>' \
              f'<br>Your one-stop online shop, where you can get all you are looking for with ease <br><br>' \
              f'<br>Click the button below to start SHOPPING! 🥳</p>' \
              f'<div class="order-btn"><a href="{frontend_link}">Get Started </a></div>'

    subject = "Welcome to Payarena Mall"
    contents = render(None, 'welcome_email.html', context={'message': message}).content.decode('utf-8')

    send_email(contents, email, subject)
    return True


def shopper_order_status_email(order_product):
    customer = order_product.order.customer
    order_no = order_product.order_id
    seller = order_product.product_detail.product.store.name
    product_image = order_product.product_detail.product.image.get_image_url()
    product_name = order_product.product_detail.product.name
    address = order_product.order.address.get_full_address()
    email = customer.user.email

    content = f'<div class="delivery-container"><div class="delivery-info"><p>Your Order #{order_no} has been ' \
              f'{order_product.status}</p></div></div><div class="merchant-letter"><p class="letter-header">' \
              f'Dear Esteemed Customer, </p><br><br><p class="letter-body">Thank you for shopping with PayArena Mall.' \
              f'<br><br>Click the button below to the indicate if your order with No #{order_no} has ' \
              f'been {order_product.status} by the seller: <span>{seller}</span></p><div class="order-btn">' \
              f'<a href="#">Confirm Order Status</a></div></div><div class="product-info"><div class="product">' \
              f'<p>Product</p><div class="product-img-details"><img src="{product_image}" alt="">' \
              f'<div class="product-details"><h3 class="product-name">{product_name}</h3>' \
              f'<p>VENDOR:<span>{seller}</span></p></div></div></div><div class="quantity"><p>Quantity</p>' \
              f'<p class="quantity-num">{order_product.quantity}</p></div><div class="price"><p>Price</p>' \
              f'<p class="price-num">NGN<span> {order_product.total}</span></p></div></div>' \
              f'<div class="shipping-info"><div class="shipping"><p>Shipping:</p>' \
              f'<p>Delivery by {order_product.order.shipper_name}</p></div><div class="shipping-address">' \
              f'<p>Shipping Address:</p><div class="shipping-address-info"><p>{address}</p>' \
              f'<p>{customer.phone_number}</p><p>{customer.user.email}</p></div></div></div>'

    subject = "Order Status"
    contents = render(None, 'shopper_order_status.html', context={'message': content}).content.decode('utf-8')

    send_email(contents, email, subject)
    return True

