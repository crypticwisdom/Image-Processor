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


def merge_carts(*, cart_uid, user):
    try:
        # Get Cart by cart_uid
        cart_instance = Cart.objects.get(cart_uid=cart_uid, status="open")
        print(cart_instance, cart_uid, "------------")

        # Filter CartProduct where cart_instance is found/connected to.
        cart_product_query = CartProduct.objects.filter(cart=cart_instance)

        # Get "open" cart that belongs to the user logged-in
        print("=====================", cart_product_query)

        user_old_cart = Cart.objects.filter(user=user, status="open").first()
        # if same product matches in the 2 carts, then increament the new cart by the number of that particular product
        # inside of the order cart.

        # if cart_product_query.count() > user_old_cart:
            # for product in cart_product_query:
                # if

        print(user_old_cart, "[[[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]")
        if user_old_cart:
            print(user_old_cart, "is not empty")
            for cart_product in cart_product_query:
                cart_p = CartProduct.objects.get(id=cart_product.id)
                print(cart_product.id, cart_p, "---------------------")

                old_cart = Cart.objects.get(id=user_old_cart.id)
                print("old cart in loop")

                cart_p.cart = old_cart
                cart_p.save()
                print(cart_p.cart)
                print("cart product has been added into CART", cart_p)

                # Delete new cart.
            cart_instance.delete()
        else:
            print(user_old_cart, "is empty")

        # print(cart_product_query)
        return True, "Success"
    except (Exception, ) as err:
        print(err, "-------------- 2 ---------------")
        return False, f"{err}"

