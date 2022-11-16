import re

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from account.models import Profile
from ecommerce.models import Product, ProductDetail, Cart, CartProduct, CartBill
import uuid
from django.utils import timezone
from threading import Thread
from ecommerce.shopper_email import shopper_signup_verification_email


def send_shopper_verification_email(email, profile):
    try:
        # Send Verification code
        profile.verification_code = uuid.uuid1()
        profile.code_expiration_date = timezone.now() + timezone.timedelta(minutes=15)
        profile.save()

        Thread(target=shopper_signup_verification_email,
               kwargs={"email": email, "profile": profile}).start()
        return True
    except (Exception,) as err:
        print(err)
        # LOG ERROR
        return False


def create_account(email, phone_number, password, first_name, last_name):
    try:
        user_instance = User.objects.create(
            username=email, email=email, password=make_password(password), first_name=first_name, last_name=last_name
        )
        if user_instance:
            profile = Profile.objects.create(user=user_instance, phone_number=phone_number)
            if not profile:
                return False, "An error occurred while creating a profile for this user"
            return True, profile
        else:
            return False, "User not created"
    except (Exception,) as err:
        # Log error
        print(err)
        return False, "An error occurred during user creation"


def validate_email(email):
    try:
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(regex, email):
            return True
        return False
    except (TypeError, Exception) as err:
        # Log error
        return False


def merge_carts(cart_uid, user):
    try:
        # Get Cart by cart_uid
        """
            - If user 
        """
        if Cart.objects.filter(cart_uid=cart_uid, status="open").exists():
            cart_instance = Cart.objects.get(cart_uid=cart_uid, status="open")

            # Filter CartProduct where cart_instance is found/connected to.
            new_cart_products = CartProduct.objects.filter(cart=cart_instance)

            if len(new_cart_products) < 1:
                cart_instance.delete()

            # Get "open" cart that belongs to the user logged-in
            if Cart.objects.filter(user=user, status="open").exists():
                # Since cart with this user is found, then perform merge with both new and old carts.

                # - Get cart and cart products relating to the user.
                user_old_cart = Cart.objects.get(user=user, status="open")
                user_old_cart_products = CartProduct.objects.filter(cart=user_old_cart)

                if len(user_old_cart_products) < 1:
                    user_old_cart.delete()

                if len(user_old_cart_products) >= len(new_cart_products):
                    # If length of old cart is > or equal to length of new cart then, merge cart and delete new_cart.
                    # - loop through carts.

                    for old_item in user_old_cart_products:
                        # check if 'old_item' is in New Cart
                        # print(old_item)

                        for new_item in new_cart_products:

                            # print(new_item.product_detail.product.id, '---', old_item.product_detail.product.id, "--")
                            if new_item.product_detail.product.id == old_item.product_detail.product.id:
                                #  if product
                                print("found")
                                new_item_quantity, old_item_quantity = new_item.quantity, old_item.quantity
                                item_stock_sum = new_item_quantity + old_item_quantity

                                # check if this item (cart product is available in the summed quantity)
                                # 'new_item.product_detail.stock' can be swapped with 'old_item.product_detail.stock'
                                if old_item.product_detail.stock == item_stock_sum:
                                    # If product is enough in stock.
                                    print("available")
                                    # merge cart to old_cart (which is the cart linked to a user instance)
                                else:
                                    # If product is not available in stock.
                                    print("not enough")
                                print(new_item_quantity, old_item_quantity, "-==-==-")
                            else:
                                print("some")
                    #     for i in user_old_cart_products:
                    #         print(old_item.name, i.name)
                    #     cart.
                    # delete cart so there should be 1 cart for the user.

                else:
                    print("----")
                    # for item in new_cart_products:
                    #     ...
                    # print(new_cart_products, user_old_cart_products, "-----------------")
                    ...
            else:
                # Since cart with user is not found then, assign the current user to the new cart.
                cart_instance.user = user
                cart_instance.cart_uid = ""
                cart_instance.save()
                # working.

        # print(cart_product_query)
        return True, "Success"
    except (Exception,) as err:
        print(err, "-------------- 2 ---------------")
        return False, f"{err}"

