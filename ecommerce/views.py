from django.shortcuts import render
from django.views.generic import ListView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.views import APIView
from django.utils import timezone
from .serializers import MallProductSerializer, AllCategoriesSerializer, MallCategorySerializer, MallDealSerializer
from .models import ProductCategory, Product, ProductDetail, Cart, CartProduct, Promo
from ecommerce.pagination import CustomPagination
import uuid
from .utils import check_cart, create_cart_product, perform_operation


# from ecommerce.utils import add_minus_remove_product_check


# Create your views here.
class MallLandPageView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            response, response_container, start_date = list(), dict(), timezone.datetime.today()
            start_date = timezone.datetime.today()

            # (1) Deals of the day: percent, is_featured, prod. image, prod. id, prod. name, rate, price
            deal_end_date = timezone.timedelta(days=1)
            deals_query_set = Promo.objects.filter(created_on__date__gte=start_date - deal_end_date,
                                                   promo_type="deal").order_by("-id")[:5]
            response_container["deals_of_the_day"] = MallDealSerializer(deals_query_set, many=True).data

            # (2) Hot New Arrivals in last 3 days
            end_date1 = timezone.timedelta(days=3)
            hot_new_arrivals = Product.objects.filter(created_on__date__gte=start_date - end_date1)  # 3 days ago
            arrival_serializer = MallProductSerializer(hot_new_arrivals, many=True).data
            response_container["hot_new_arrivals"] = arrival_serializer

            # (3) Top-selling
            end_date2 = timezone.timedelta(weeks=1)
            # sale count would be updated by the Admin.
            # here, we would fetch the updated results made by the admin.
            top_selling = Product.objects.filter(sale_count=0, created_on__date__gte=start_date - end_date2)
            top_selling_serializer = MallProductSerializer(top_selling, many=True).data
            response_container["top_selling"] = top_selling_serializer[:15]

            # (4) Top categories of the month updated
            end_date3 = timezone.timedelta(weeks=4)
            # sale-count would be manually updated by the Admin on his end.
            # here, we would fetch the updated results made by the admin.
            top_selling = Product.objects.filter(sale_count=0, created_on__date__gte=start_date - end_date3)
            categories_serializer = MallCategorySerializer(top_selling, many=True).data
            response_container["top_monthly_categories"] = categories_serializer

            # (5) Recommended Products
            recommended = MallProductSerializer(Product.objects.filter(is_featured=True), many=True).data
            response_container["recommended_products"] = recommended[:5]

            response.append(response_container)
            return Response({"detail": response}, status=HTTP_200_OK)
        except (Exception,) as err:
            print(err)
            # LOG
            return Response({"detail": str(err)}, status=HTTP_400_BAD_REQUEST)


class AllCategoriesView(APIView, CustomPagination):
    permission_classes = []

    def get(self, request):
        try:
            query_set = ProductCategory.objects.filter().order_by("-id")
            paginate_queryset = self.paginate_queryset(query_set, request)
            serialized_data = AllCategoriesSerializer(paginate_queryset, many=True).data
            data = self.get_paginated_response(serialized_data).data
            return Response({"detail": data}, status=HTTP_200_OK)

        except (Exception,) as err:
            return Response({"detail": str(err)}, status=HTTP_400_BAD_REQUEST)


class TopSellingProductsView(APIView, CustomPagination):
    permission_classes = []

    def get(self, request):
        try:
            start_date = timezone.datetime.today()
            end_date2 = timezone.timedelta(weeks=1)

            queryset = Product.objects.filter(sale_count=0, created_on__date__gte=start_date - end_date2).order_by(
                "-id")
            paginated_query = self.paginate_queryset(queryset, request)
            data = self.get_paginated_response(MallProductSerializer(paginated_query, many=True).data).data

            return Response({"detail": data}, status=HTTP_200_OK)
        except (Exception,) as err:
            print(err)
            # LOG ERROR
            return Response({"detail": str(err)}, status=HTTP_400_BAD_REQUEST)


class RecommendedProductView(APIView, CustomPagination):
    permission_classes = []

    def get(self, request):
        try:
            query_set = Product.objects.filter(is_featured=True).order_by("-id")
            data = MallProductSerializer(query_set, many=True).data

            paginated_query = self.paginate_queryset(query_set, request)
            data = self.get_paginated_response(data=data).data
            return Response({"detail": data}, status=HTTP_200_OK)
        except (Exception,) as err:
            print(err)
            # LOG ERROR
            return Response({"detail": str(err)}, status=HTTP_400_BAD_REQUEST)


class CartProductOperationsView(APIView):
    """
        Used for creating cart and adding item, increasing, decreasing and removing cart-product to/from cart,
        it receives a Cart-Product ID, for either of the cases.
        A user should not be able to add more than the available stocks for the product.
    """
    permission_classes = []

    def post(self, request):
        try:
            """
                1 known issue: If this endpoint has been called to create and add the first product, the second call of 
                this endpoint without cart id or uid will also create another cart and cart-product.
                So, frontend or anyone needs to call this endpoint with cart id or uid the second time.
                
                - 'operation_param' must be passed after cart has been created for the first time.
                - Pass 'operation_param" = '+' if user wants to add the product more than once.
            """

            product_id = request.data.get("product_id", None)
            cart_uid = request.data.get("cart_uid", None)
            cart_id = request.data.get("cart_id", None)
            operation_param = request.data.get("operation_param", None)

            if product_id is None:
                return Response({"detail": "Product's ID was not provided"}, status=HTTP_400_BAD_REQUEST)

            if operation_param is None:
                return Response({"detail": "Specify operation with one of these -, +, or remove"},
                                status=HTTP_400_BAD_REQUEST)

            # user is not authenticated, cart_id or uid was not given then, create a new cart.
            if not request.user.is_authenticated:
                # request for cart id or uid since user is not authenticated.
                # If 'cart_uid' or 'cart_id' is not given and 'operation_param' == '+'
                if not (cart_uid or cart_id) and operation_param == "+":
                    # Create cart
                    cart = Cart.objects.create(cart_uid=uuid.uuid4())

                    success, response = create_cart_product(product_id=product_id, cart=cart)
                    if success:
                        return Response({"detail": "Successfully created a cart and product has been added",
                                         "data": {"cart_uid": cart.cart_uid, "cart_id": cart.id}},
                                        status=HTTP_201_CREATED)
                    else:
                        return Response({"detail": f"{response}"}, status=HTTP_400_BAD_REQUEST)
                else:
                    # That means this user is not authenticated, but cart id / uid and a product_id is passed.
                    success, msg = check_cart(cart_id=cart_id, cart_uid=cart_uid)

                    if not success:
                        # Create cart
                        if not (cart_uid or cart_id) and operation_param == "+":
                            # create a cart and return cart id and uid
                            # Return 'cart_id' and 'uid' if 'cart_id' or 'cart_uid' is not given
                            # Create CART

                            if cart_id:
                                cart = Cart.objects.get(id=cart_id, status='open')
                            elif cart_uid:
                                Cart.objects.get(cart_uid=cart_uid, status='open')

                            success, response = create_cart_product(product_id=product_id, cart=cart)
                            if success:
                                return Response({"detail": "Successfully created a cart and product has been added",
                                                 "data": {"cart_uid": cart.cart_uid, "cart_id": cart.id}},
                                                status=HTTP_201_CREATED)
                            else:
                                return Response({"detail": f"{response}"}, status=HTTP_400_BAD_REQUEST)
                    else:
                        # get the product_detail
                        # check the operation the user wants to perform
                        product_detail = ProductDetail.objects.get(product__id=product_id)
                        cart = None

                        if cart_id:
                            cart = Cart.objects.get(id=cart_id, status='open')
                        elif cart_uid:
                            cart = Cart.objects.get(cart_uid=cart_uid, status='open')

                        # Get cart products that belongs to that cart.
                        cart_products = CartProduct.objects.all().filter(cart=cart)
                        # Loop through the cart-products to see if this product already exists.
                        # If True then, Simply increase the item/product by 1.
                        # Else, Add the item/product to Cart.

                        check_response = list()

                        for cart_product in cart_products:
                            if cart_product.product_detail == product_detail:
                                check_response.append(True)

                                # what operation to perform ?
                                operation_status, msg = perform_operation(operation_param, product_detail, cart_product)
                                if operation_status is False:
                                    return Response({"detail": f"{msg}"}, status=HTTP_400_BAD_REQUEST)
                                else:
                                    return Response({"detail": f"{msg}"}, status=HTTP_200_OK)

                            else:
                                # update check response
                                check_response.append(False)

                        # Add product to cart if product is not found inside the cart.

                        if operation_param == '+':
                            cart_product = CartProduct.objects.create(
                                cart=cart, product_detail=product_detail, price=product_detail.price,
                                discount=product_detail.discount, quantity=1)
                            return Response({"detail": "Product has been added to cart"}, status=HTTP_201_CREATED)
            else:
                # That means this user is authenticated, now a cart id / uid is not important.
                # cart operation using the cart's id or uid
                # - check if any cart exists with this user

                user = request.user
                success, response = check_cart(user)

                if not success:
                    # create cart
                    if not (cart_uid or cart_id) and operation_param == "+":
                        # create a cart and return  uid
                        # if 'cart_id' or 'cart_uid' is not present it means to create a cart and return 'cart_id'

                        # Create CART
                        cart = Cart.objects.create(user=user)

                        success, response = create_cart_product(product_id=product_id, cart=cart)
                        if success:
                            # cart id is returned since Cart's created by logged in user does not need a cart uid.
                            return Response({"detail": "Successfully created a cart and product has been added",
                                             "data": {"cart_id": cart.id}},
                                            status=HTTP_201_CREATED)
                        else:
                            return Response({"detail": f"{response}"}, status=HTTP_400_BAD_REQUEST)
                else:
                    # get the product_detail
                    # check the operation the user wants to perform
                    product_detail = ProductDetail.objects.get(product__id=product_id)
                    cart = Cart.objects.get(user=user, status='open')

                    # Get cart products that belongs to that cart.
                    cart_products = CartProduct.objects.all().filter(cart=cart)

                    # Loop through the cart-products to see if this product already exists.
                    # If True then, Simply increase the item/product by 1.
                    # Else, Add the item/product to Cart.

                    check_response = list()
                    for cart_product in cart_products:

                        if cart_product.product_detail == product_detail:
                            check_response.append(True)

                            # what operation to perform ?
                            operation_status, msg = perform_operation(operation_param, product_detail, cart_product)
                            if operation_status is False:
                                return Response({"detail": f"{msg}"}, status=HTTP_400_BAD_REQUEST)
                            else:
                                return Response({"detail": f"{msg}"}, status=HTTP_200_OK)

                        else:
                            # update check response
                            check_response.append(False)

                    # Add product to cart if product is not found inside the cart.
                    if operation_param == '+' and True not in check_response:
                        success, response = create_cart_product(product_id=product_id, cart=cart)
                        if success:
                            return Response({"detail": "Product has been added to cart"}, status=HTTP_201_CREATED)
                        else:
                            return Response({"detail": f"{response}"}, status=HTTP_400_BAD_REQUEST)

            return Response({"detail": "No Operation performed"}, status=HTTP_400_BAD_REQUEST)
        except (Exception,) as err:
            return Response({"detail": str(err)}, status=HTTP_400_BAD_REQUEST)


class CartView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            cart_uid = request.data.get("cart_uid", None)
            cart_id = request.data.get("cart_id", None)

            cart = None
            print(cart, request.user)
            if request.user.is_authenticated:
                cart = Cart.objects.get(user=request.user, status='open')
            else:
                if cart_uid is None and cart_id is None:
                    return Response({"detail": "Cart UID or ID is required"}, status=HTTP_400_BAD_REQUEST)

                if cart_id:
                    cart = Cart.objects.get(id=cart_id, status='open')
                elif cart_uid:
                    Cart.objects.get(cart_uid=cart_uid, status='open')

            print(cart, "--------------------")
            cart_products = CartProduct.objects.all().filter(cart=cart)
            print(cart_products)

            # # ser = CartProductSerializer
            from .serializers import CartProductSerializer

            # print(cart_products)
            #
            ser = CartProductSerializer(cart_products, many=True).data

            return Response({"detail": "Positive response", "data": {
                "cart_count": cart_products.count(),
                "ser": ser
            }}, status=HTTP_200_OK)
        except (Exception,) as err:
            print(err)
            return Response({"detail": f"{err}"}, status=HTTP_400_BAD_REQUEST)
