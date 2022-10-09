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
from .serializers import ProductSerializer, CategoriesSerializer, MallDealSerializer, ProductWishlistSerializer
from .models import ProductCategory, Product, ProductDetail, Cart, CartProduct, Promo, ProductWishlist
from ecommerce.pagination import CustomPagination, DesktopResultsSetPagination
import uuid
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

            # (3) Top-selling
            end_date2 = timezone.timedelta(weeks=1)
            # sale count would be updated by the Admin.
            # here, we would fetch the updated results made by the admin.
            top_selling = Product.objects.filter(sale_count=0, created_on__date__gte=start_date - end_date2, status="active")
            top_selling_serializer = ProductSerializer(top_selling, many=True).data
            response_container["top_selling"] = top_selling_serializer[:15]

            # (4) Top categories of the month updated
            end_date3 = timezone.timedelta(weeks=4)
            # sale-count would be manually updated by the Admin on his end.
            # here, we would fetch the updated results made by the admin.
            top_selling = Product.objects.filter(sale_count=0, created_on__date__gte=start_date - end_date3)
            categories_serializer = ProductSerializer(top_selling, many=True, context={"request": request}).data
            response_container["top_monthly_categories"] = categories_serializer

            # (5) Recommended Products
            recommended = ProductSerializer(Product.objects.filter(is_featured=True), many=True, context={"request": request}).data
            response_container["recommended_products"] = recommended[:5]

            # (6) All categories - to include sub categories and product types
            categories = CategoriesSerializer(ProductCategory.objects.filter(parent=True), many=True, context={"request": request}).data
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

            # If cart 'id' or 'uid' is present in the request, it means there's a cart created already
            if cart_uid or cart_id:
                # Get CART with CART's UID or ID

                if Cart.objects.filter(cart_uid=cart_uid).exists() or Cart.objects.filter(id=cart_id).exists():

                    # check if product exist add to cart
                    cart = None
                    if cart_uid:
                        cart = Cart.objects.get(cart_uid=cart_uid)
                    elif cart_id:
                        cart = Cart.objects.get(id=cart_id)

                    if Product.objects.filter(id=product_id).exists():

                        product = Product.objects.get(id=product_id)
                        product_detail = ProductDetail.objects.get(product=product)

                        # Get cart products that belongs to that cart.
                        cart_products = CartProduct.objects.all().filter(cart=cart)

                        # Loop through the cart-products to see if this product already exists.
                        # If True then, Simply increase the item/product by 1.
                        # Else, Add the item/product to Cart.

                        check_response = list()
                        for item in cart_products:
                            if item.product_detail == product_detail:
                                # Run a check to see if the available quantity in merchant's store is enough for this
                                # cart-product. (Run check before increasing product quantity to see if it is available)

                                # increase this item's 'cart-product' quality by 1 and sum their total.
                                # item.quantity

                                if not (product_detail.stock > item.quantity):
                                    return Response({"detail": "This product is out of stock",
                                                     "data": {"cart_uid": cart.cart_uid, "cart_id": cart.id}},
                                                    status=status.HTTP_400_BAD_REQUEST)

                                # Operations for increase, reduce and remove

                                if operation_param not in ("+", "-", "remove"):
                                    return Response({"detail": "Invalid Operation Parameter, expected -, +, or remove"},
                                                    status=status.HTTP_400_BAD_REQUEST)

                                elif operation_param == "-" or operation_param == "remove":
                                    if item.quantity == 1 or operation_param == "remove":
                                        item.delete()
                                        return Response({"detail": "Product has been removed from cart",
                                                         "data": {"cart_uid": cart.cart_uid, "cart_id": cart.id}})

                                    elif operation_param == "-":
                                        item.quantity -= 1
                                        item.save()
                                        return Response({"detail": "Product has been reduced from cart",
                                                         "data": {"cart_uid": cart.cart_uid, "cart_id": cart.id}})

                                else:
                                    # This block executes only if operation_param is '+'
                                    # And the program continues/flow downward.
                                    pass

                                item.quantity += 1
                                item.price = item.quantity * product_detail.price
                                item.save()

                                check_response.append(True)
                                return Response({"detail": "Added to cart",
                                                 "data": {"cart_uid": cart.cart_uid, "cart_id": cart.id}},
                                                status=status.HTTP_201_CREATED)
                            else:
                                # Update 'check_response' to False, which means each item wasn't found
                                check_response.append(False)

                        # if all elements of 'check_response' is False and the len. of 'check_response' is equal to the
                        # 'cart_products' query set. which means the product is not found in the 'cart_products'
                        if (True not in check_response) and len(check_response) == cart_products.count():

                            if operation_param == "-" or operation_param == "remove":
                                return Response({"detail": f"Can't add product by passing {operation_param} operation",
                                                 "data": {"cart_uid": cart.cart_uid, "cart_id": cart.id}},
                                                status=status.HTTP_400_BAD_REQUEST)

                            # Add product to cart.
                            cart_product = CartProduct.objects.create(cart=cart, product_detail=product_detail,
                                                                      price=product_detail.price, quantity=1,
                                                                      discount=product_detail.discount)

                            return Response({"detail": "Successfully added product",
                                             "data": {"cart_uid": cart.cart_uid, "cart_id": cart.id}},
                                            status=status.HTTP_201_CREATED)
            else:
                # if 'cart_id' or 'cart_uid' is not present it means to create a cart and return 'cart_id' and 'uid'
                # Create CART
                cart = Cart.objects.create(cart_uid=uuid.uuid4())

                # Get product and product detail with the 'product_id'

                if Product.objects.filter(id=product_id).exists():

                    product = Product.objects.get(id=product_id)
                    product_detail = ProductDetail.objects.get(product=product)

                    # Cart Product
                    cart_product = CartProduct.objects.create(
                        cart=cart, product_detail=product_detail, price=product_detail.price,
                        discount=product_detail.discount, quantity=1)

                    return Response({"detail": "Successfully created a cart and product has been added",
                                     "data": {"cart_uid": cart.cart_uid, "cart_id": cart.id}},
                                    status=status.HTTP_201_CREATED)
                else:
                    return Response({"detail": "Product ID does not match"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"detail": "Invalid Product ID"}, status=status.HTTP_400_BAD_REQUEST)
        except (Exception,) as err:
            return Response({"detail": str(err)}, status=status.HTTP_400_BAD_REQUEST)


class CartView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            cart_uid_or_id = request.GET.get("cart_uid_or_id", None)

            if cart_uid_or_id is not None:
                carts = Cart.objects.filter(id=cart_uid_or_id) or Cart.objects.filter(cart_uid=cart_uid_or_id)

                # cart_product =
        except (Exception, ) as err:
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

