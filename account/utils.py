import re

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from account.models import Profile
from ecommerce.models import Product, ProductDetail, Cart, CartProduct, CartBill


def create_account(username, email, phone_number, password):
    try:
        user_instance = User.objects.create(username=username, email=email, password=make_password(password))
        if user_instance:
            profile = Profile.objects.create(user=user_instance, phone_number=phone_number)
            if not profile:
                return False, "An error occurred while creating a profile for this user"
            return True, profile
        else:
            return False, "User not created"
    except (Exception, ) as err:
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
            new_cart_products = CartProduct.objects.all().filter(cart=cart_instance)

            if len(new_cart_products) < 1:
                cart_instance.delete()

            # Get "open" cart that belongs to the user logged-in
            if Cart.objects.filter(user=user, status="open").exists():
                # Since cart with this user is found, then perform merge with both new and old carts.

                # - Get cart and cart products relating to the user.
                user_old_cart = Cart.objects.get(user=user, status="open")
                user_old_cart_products = CartProduct.objects.all().filter(cart=user_old_cart)

                if len(user_old_cart_products) < 1:
                    user_old_cart.delete()

                if len(new_cart_products) <= len(user_old_cart_products):
                    # If length of new cart is < or equal to length of old cart then, merge cart and delete new_cart.

                    # - loop through carts
                    for new_item in new_cart_products:
                        # cart.
                        ...
                    # delete cart so there should be 1 cart for the user.

                else:
                    for item in user_old_cart_products:
                        ...
                print(new_cart_products, user_old_cart_products, "-----------------")
            else:
                # Since cart with user is not found then, assign the current user to the new cart.
                cart_instance.user = user
                cart_instance.cart_uid = ""
                cart_instance.save()
                # working.


        # print(cart_product_query)
        return True, "Success"
    except (Exception, ) as err:
        print(err, "-------------- 2 ---------------")
        return False, f"{err}"

