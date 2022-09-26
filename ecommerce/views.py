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


# Create your views here.


class MallLandPageView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            response, response_container, start_date = list(), dict(), timezone.datetime.today()
            start_date = timezone.datetime.today()

            # (1) Deals of the day: percent, is_featured, prod. image, prod. id, prod. name, rate, price
            deal_end_date = timezone.timedelta(days=1)
            deals_query_set = Promo.objects.filter(created_on__date__gte=start_date - deal_end_date).order_by("-id")[:5]
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


class AddToCartView(APIView):
    """
        AddToCartView: This view is used to create a cart with an initial item and PUT item to cart.
            POST: Creates a new cart and adds the product to cart. returns --> cart_uid and cart's ID.
            PUT: Adds an Item to cart. Returns --> detail message.
    """
    """
        merge carts
    """
    permission_classes = []

    def post(self, request):
        try:
            product_id = request.data.get("product_id", None)

            if product_id is None:
                return Response({"detail": "Product's ID was not provided"}, status=HTTP_400_BAD_REQUEST)

            if request.user.is_authenticated:
                # Create a cart instance with the Cart and CartProduct
                cart = Cart.objects.create(user=request.user)
            else:
                cart = Cart.objects.create(cart_uid=uuid.uuid4())
            # Get the product and link it's "product_detail" instance to a new Cart instance.

            product_instance = Product.objects.get(id=product_id)
            product_detail = ProductDetail.objects.get(product=product_instance)

            cart_product = CartProduct.objects.create(
                cart=cart, product_detail=product_detail, quantity=1, price=product_detail.price,
                discount=product_detail.discount  # should delivery fee be set by the Admin and Also ?
            )
            # Return cart_id and cart_uid:
            # really important for cases where user needs to access his/her cart from another device, all he needs is
            # his cart_uid or cart_id.
            return Response({"detail": {"cart_uid": cart.cart_uid, "cart_id": cart.id}}, status=HTTP_201_CREATED)
        except (Exception,) as err:
            return Response({"detail": str(err)}, status=HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            cart_uid_or_id = request.data.get("cart_uid_or_id", None)
            product_id = request.data.get("product_id", None)

            if cart_uid_or_id is None:
                return Response({"detail": "Cart ID or UID is required"}, status=HTTP_400_BAD_REQUEST)

            if product_id is None:
                return Response({"detail": "Product ID is required"}, status=HTTP_400_BAD_REQUEST)

            cart = Cart.objects.get(cart_uid=cart_uid_or_id) or Cart.objects.get(id=cart_uid_or_id)

            product_instance = Product.objects.get(id=product_id)
            product_detail = ProductDetail.objects.get(product=product_instance)

            cart_product = CartProduct.objects.create(
                cart=cart, product_detail=product_detail, quantity=1, price=product_detail.price,
                discount=product_detail.discount  # should delivery fee be set by the Admin and Also ?
            )

            return Response({"detail": "Product has been added to cart"}, status=HTTP_200_OK)
        except (Exception, ) as err:
            return Response({"detail": str(err)}, status=HTTP_400_BAD_REQUEST)


class CartProductOperationsView(APIView):
    permission_classes = []

    """
        Used for increasing, decreasing and removing cart-product to/from cart, it receives a Cart-Product ID, 
        for either of the cases.
        A user should not be able to add more than the available stocks for the product.
    """
    """
    - Ashavin said i should handle the increment and decrement in the 'AddToCartView' post request.
        So that if a newly item was added twice it should increment it instead of adding it as a second item in the cart
    - Add only wallet ID field to user profile.
    - write an end point for Related Products.
    """
    def put(self, request):
        try:
            ...
        except (Exception, ) as err:
            ...
