from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from django.utils import timezone

from .filters import ProductFilter
from .serializers import ProductSerializer, CategoriesSerializer, MallDealSerializer, ProductWishlistSerializer, \
    CartProductSerializer

from .models import ProductCategory, Product, ProductDetail, Cart, CartProduct, Promo, ProductWishlist
from ecommerce.pagination import CustomPagination, DesktopResultsSetPagination
import uuid
from .utils import check_cart, create_cart_product, perform_operation, top_weekly_products, top_monthly_categories

# from ecommerce.utils import add_minus_remove_product_check


# Create your views here.
from .utils import sorted_queryset


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
            hot_new_arrivals = Product.objects.filter(created_on__date__gte=start_date - end_date1, status="active")  # 3 days ago
            arrival_serializer = ProductSerializer(hot_new_arrivals, many=True).data
            response_container["hot_new_arrivals"] = arrival_serializer

            # (3) Top weekly selling products
            top_products = top_weekly_products()
            response_container["top_selling"] = top_products

            # (4) Top categories of the month
            top_monthly_cat = top_monthly_categories()
            response_container["top_monthly_categories"] = top_monthly_cat

            # (5) Recommended Products
            recommended = ProductSerializer(Product.objects.filter(
                is_featured=True, status="active", store__is_active=True), many=True, context={"request": request}
            ).data
            response_container["recommended_products"] = recommended[:5]

            # (6) All categories - to include sub categories and product types
            categories = CategoriesSerializer(
                ProductCategory.objects.filter(parent=None), many=True, context={"request": request}
            ).data
            response_container["categories"] = categories

            response.append(response_container)
            return Response({"detail": response})
        except Exception as err:
            print(err)
            # LOG
            return Response({"detail": str(err)}, status=status.HTTP_400_BAD_REQUEST)


class CategoriesView(APIView, CustomPagination):
    permission_classes = []

    def get(self, request):
        try:
            query_set = ProductCategory.objects.filter(parent=None).order_by("-id")
            paginate_queryset = self.paginate_queryset(query_set, request)
            serialized_data = CategoriesSerializer(paginate_queryset, many=True, context={"request": request}).data
            data = self.get_paginated_response(serialized_data).data
            return Response({"detail": data})

        except (Exception,) as err:
            return Response({"detail": str(err)}, status=status.HTTP_400_BAD_REQUEST)


class TopSellingProductsView(APIView, CustomPagination):
    permission_classes = []

    def get(self, request):
        try:
            start_date = timezone.datetime.today()
            end_date2 = timezone.timedelta(weeks=1)

            queryset = Product.objects.filter(sale_count=0, created_on__date__gte=start_date - end_date2).order_by(
                "-id")
            paginated_query = self.paginate_queryset(queryset, request)
            data = self.get_paginated_response(ProductSerializer(paginated_query, many=True).data).data

            return Response({"detail": data})
        except (Exception,) as err:
            print(err)
            # LOG ERROR
            return Response({"detail": str(err)}, status=status.HTTP_400_BAD_REQUEST)


class RecommendedProductView(APIView, CustomPagination):
    permission_classes = []

    def get(self, request):
        try:
            query_set = Product.objects.filter(is_featured=True).order_by("-id")
            data = ProductSerializer(query_set, many=True).data

            paginated_query = self.paginate_queryset(query_set, request)
            data = self.get_paginated_response(data=data).data
            return Response({"detail": data})
        except (Exception,) as err:
            print(err)
            # LOG ERROR
            return Response({"detail": str(err)}, status=status.HTTP_400_BAD_REQUEST)



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
                return Response({"detail": "Product's ID was not provided"}, status=status.HTTP_400_BAD_REQUEST)

            if operation_param is None:
                return Response({"detail": "Specify operation with one of these -, +, or remove"},
                                status=status.HTTP_400_BAD_REQUEST)
            # ==================================== Good ==============================================

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
                                        status=status.HTTP_201_CREATED)
                    else:
                        return Response({"detail": f"{response}"}, status=status.HTTP_400_BAD_REQUEST)
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
                                                status=status.HTTP_201_CREATED)
                            else:
                                return Response({"detail": f"{response}"}, status=status.HTTP_400_BAD_REQUEST)
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
                                    return Response({"detail": f"{msg}"}, status=status.HTTP_400_BAD_REQUEST)
                                else:
                                    return Response({"detail": f"{msg}"}, status=status.HTTP_200_OK)

                            else:
                                # update check response
                                check_response.append(False)

                        # Add product to cart if product is not found inside the cart.
                        if operation_param == '+':
                            cart_product = CartProduct.objects.create(
                                cart=cart, product_detail=product_detail, price=product_detail.price,
                                discount=product_detail.discount, quantity=1)
                            return Response({"detail": "Product has been added to cart"}, status=status.HTTP_201_CREATED)
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
                                             "data": {"cart_id": cart.id}}, status=status.HTTP_201_CREATED)
                        else:
                            return Response({"detail": f"{response}"}, status=status.HTTP_400_BAD_REQUEST)
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
                                return Response({"detail": f"{msg}"}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                return Response({"detail": f"{msg}"})

                        else:
                            # update check response
                            check_response.append(False)

                    # Add product to cart if product is not found inside the cart.
                    if operation_param == '+' and True not in check_response:
                        success, response = create_cart_product(product_id=product_id, cart=cart)
                        if success:
                            return Response({"detail": "Product has been added to cart"}, status=status.HTTP_201_CREATED)
                        else:
                            return Response({"detail": f"{response}"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "No Operation performed"}, status=status.HTTP_400_BAD_REQUEST)

        except (Exception,) as err:
            return Response({"detail": str(err)}, status=status.HTTP_400_BAD_REQUEST)


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
                    return Response({"detail": "Cart UID or ID is required"}, status=status.HTTP_400_BAD_REQUEST)

                if cart_id:
                    cart = Cart.objects.get(id=cart_id, status='open')
                elif cart_uid:
                    cart = Cart.objects.get(cart_uid=cart_uid, status='open')

            cart_products = CartProduct.objects.all().filter(cart=cart)
            print(cart_products)

            # ser = CartProductSerializer

            # print(cart_products)
            #
            ser = CartProductSerializer(cart_products, many=True).data

            return Response({"detail": "Positive response", "data": {
                "cart_count": cart_products.count(),
                "ser": ser
            }}, status=status.HTTP_200_OK)
        except (Exception,) as err:
            print(err)
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)


class FilteredSearchView(generics.ListAPIView):
    permission_classes = []
    pagination_class = DesktopResultsSetPagination
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_class = ProductFilter

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        order_by = self.request.GET.get('sort_by', '')

        query = Q(status='active', store__is_active=True)

        if search:
            query &= Q(name=search)

        if order_by:
            queryset = sorted_queryset(order_by, query)
            return queryset

        queryset = Product.objects.filter(query).order_by('-updated_on').distinct()
        return queryset


class ProductWishlistView(APIView):

    def post(self, request):
        product_id = request.data.get('product_id', '')
        if not product_id:
            return Response({"detail": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(pk=product_id)
            product_wishlist, created = ProductWishlist.objects.get_or_create(user=request.user, product=product)
            data = ProductWishlistSerializer(product_wishlist).data

            return Response({"detail": "Added to wishlist", "data": data})
        except Exception as ex:
            return Response({"detail": "An error occurred. Please try again", "error": str(ex)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RetrieveDeleteWishlistView(generics.RetrieveDestroyAPIView):
    pagination_class = [CustomPagination]
    serializer_class = ProductWishlistSerializer
    lookup_field = "id"

    def get_queryset(self):
        queryset = ProductWishlist.objects.filter(user=self.request.user)
        return queryset


class ProductView(APIView, CustomPagination):
    permission_classes = []

    def get(self, request, pk=None):
        try:
            if pk:
                product = Product.objects.get(id=pk, status="active", store__is_active=True)
                product.view_count += 1
                product.save()
                serializer = ProductSerializer(product, context={"request": request}).data
            else:
                prod = self.paginate_queryset(request, Product.objects.filter(status="active", store__is_active=True))
                queryset = ProductSerializer(prod, many=True, context={"request": request}).data
                serializer = self.get_paginated_response(queryset).data
            return Response(serializer)
        except Exception as err:
            return Response({"detail": "Error occurred while fetching product", "error": str(err)})





