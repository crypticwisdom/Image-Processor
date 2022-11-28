from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from django.utils import timezone
from account.models import Profile, Address
from account.utils import get_wallet_info
from store.serializers import CartSerializer
from .filters import ProductFilter
from .serializers import ProductSerializer, CategoriesSerializer, MallDealSerializer, ProductWishlistSerializer, \
    CartProductSerializer, OrderSerializer, ReturnedProductSerializer, OrderProductSerializer

from .models import ProductCategory, Product, ProductDetail, Cart, CartProduct, Promo, ProductWishlist, Order, \
    OrderProduct, ReturnReason, ReturnedProduct, ReturnProductImage
from ecommerce.pagination import CustomPagination, DesktopResultsSetPagination
import uuid
from .utils import check_cart, perform_operation, top_weekly_products, top_monthly_categories, \
    validate_product_in_cart, get_shipping_rate, order_payment, add_order_product, perform_order_cancellation, \
    perform_order_pickup, perform_order_tracking, create_or_update_cart_product
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
            hot_new_arrivals = Product.objects.filter(created_on__date__gte=start_date - end_date1,
                                                      status="active")  # 3 days ago
            arrival_serializer = ProductSerializer(hot_new_arrivals, many=True, context={"request": request}).data
            response_container["hot_new_arrivals"] = arrival_serializer

            # (3) Top weekly selling products
            top_products = top_weekly_products(request)
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
        except (Exception,) as err:
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
            data = self.get_paginated_response(ProductSerializer(paginated_query, many=True, context={"request": request}).data).data

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
            data = ProductSerializer(query_set, many=True, context={"request": request}).data

            paginated_query = self.paginate_queryset(query_set, request)
            data = self.get_paginated_response(data=data).data
            return Response({"detail": data})
        except (Exception,) as err:
            print(err)
            # LOG ERROR
            return Response({"detail": str(err)}, status=status.HTTP_400_BAD_REQUEST)


class CartProductOperationsView(APIView):
    permission_classes = []

    def post(self, request):
        try:
            variant = request.data.get("variant", [])
            cart_uid = request.data.get("cart_uid")

            if not variant:
                return Response(
                    {"detail": "Product variant is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            if request.user.is_authenticated:
                cart, _ = Cart.objects.get_or_create(user=request.user, status="open")
            else:
                if cart_uid:
                    cart = get_object_or_404(Cart, cart_uid=cart_uid)
                else:
                    cart = Cart.objects.create(cart_uid=uuid.uuid4())

            success, response = create_or_update_cart_product(variant, cart=cart)
            if success is False:
                return Response({"detail": response}, status=status.HTTP_400_BAD_REQUEST)
            # Delete cart if no item is in it
            if not CartProduct.objects.filter(cart=cart).exists():
                cart.delete()
                return Response({"detail": "Cart is empty"})

            serializer = CartSerializer(cart, context={"request": request}).data
            return Response({"detail": "Cart updated", "data": serializer})
        except Exception as err:
            return Response({"detail": "An error has occurred", "error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id=None):
        # try:
        cart = None
        if request.user.is_authenticated:
            if Cart.objects.filter(status="open", user=request.user).exists():
                cart = Cart.objects.filter(status="open", user=request.user).last()
                remaining_open_carts = Cart.objects.filter(status="open", user=request.user).exclude(id=cart.id)

                # Close other open carts
                if remaining_open_carts:
                    remaining_open_carts.update(status="discard")
        else:
            if Cart.objects.filter(status="open", cart_uid=id).exists():
                cart = Cart.objects.get(status="open", cart_uid=id)

        if not cart:
            return Response({"detail": "Cart empty"})

        serializer = CartSerializer(cart, context={"request": request}).data

        return Response({"detail": serializer}, status=status.HTTP_200_OK)
        # except (Exception,) as err:
        #     return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)


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
            query &= Q(name__icontains=search)

        if order_by:
            queryset = sorted_queryset(order_by, query)
            return queryset

        queryset = Product.objects.filter(query).order_by('-updated_on').distinct()
        return queryset


class ProductWishlistView(APIView, CustomPagination):

    def get(self, request):
        try:
            product_wishlist = ProductWishlist.objects.filter(user=request.user).order_by("-id")
            paginated_queryset = self.paginate_queryset(product_wishlist, request)
            serialized_queryset = ProductWishlistSerializer(paginated_queryset, many=True, context={"request": request}).data
            serializer = self.get_paginated_response(serialized_queryset).data
            return Response({"detail": serializer})
        except (Exception, ) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        product_id = request.data.get('product_id', '')
        if not product_id:
            return Response({"detail": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(pk=product_id)
            product_wishlist, created = ProductWishlist.objects.get_or_create(user=request.user, product=product)
            data = ProductWishlistSerializer(product_wishlist, context={"request": request}).data

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
                prod = self.paginate_queryset(Product.objects.filter(status="active", store__is_active=True), request)
                queryset = ProductSerializer(prod, many=True, context={"request": request}).data
                serializer = self.get_paginated_response(queryset).data
            return Response(serializer)
        except Exception as err:
            return Response({"detail": "Error occurred while fetching product", "error": str(err)})


class ProductCheckoutView(APIView):

    def get(self, request):
        address_id = request.GET.get("address_id")
        try:
            # Get customer profile
            customer, created = Profile.objects.get_or_create(user=request.user)
            # Validate product in cart
            validate = validate_product_in_cart(customer)
            if validate:
                return Response({"detail": validate}, status=status.HTTP_400_BAD_REQUEST)
            # Call shipping API to get rate
            shipping_rate = get_shipping_rate(customer, address_id)
            return Response(shipping_rate)
        except Exception as err:
            return Response({"detail": "An error has occurred", "error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):

        payment_method = request.data.get("payment_method")
        cart_id = request.data.get("cart_id")
        address_id = request.data.get("address_id")
        sender_town_id = request.data.get("sender_town_id")
        receiver_town_id = request.data.get("receiver_town_id")
        shipping_information = request.data.get("shipping_information")

        # Expected shipping_information payload
        # shipping_information = [
        #     {
        #         "cart_product_id": 2,
        #         "company_id": "234",
        #         "shipper": "GIGLOGISTICS",
        #         "shipping_fee": "1000"
        #     }
        # ]

        if not all([shipping_information, sender_town_id, receiver_town_id, address_id]):
            return Response({"detail": "Shipper information, address, sender town, and recipient town are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        # try:
        customer, created = Profile.objects.get_or_create(user=request.user)
        address = Address.objects.get(customer=customer, id=address_id)
        cart = Cart.objects.get(user=request.user, id=cart_id, status="open")

        for product in shipping_information:
            # Get Cart Products
            cart_product = CartProduct.objects.get(id=product["cart_product_id"], cart=cart)
            if str(product["company_id"]).isnumeric():
                cart_product.company_id = product["company_id"]
            cart_product.shipper_name = str(product["shipper"]).upper()
            cart_product.delivery_fee = product["shipping_fee"]
            cart_product.save()

        validate = validate_product_in_cart(customer)
        if validate:
            return Response({"detail": validate}, status=status.HTTP_400_BAD_REQUEST)

        # Create Order
        order, created = Order.objects.get_or_create(customer=customer, cart=cart, address=address)

        # PROCESS PAYMENT
        success, detail = order_payment(payment_method, order)
        if success is False:
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)

        # update order
        order_products = add_order_product(order)
        # Update payment method
        order_products.update(payment_method=payment_method)
        # Call pickup order request

        success, response = perform_order_pickup(order_products, address, sender_town_id, receiver_town_id)

        if success is False:
            # Process refund to customer wallet
            return Response({"detail": response}, status=status.HTTP_400_BAD_REQUEST)

        # Send order placement email to shopper
        # Send order placement email to seller
        # Send order placement email to admins

        return Response({"detail": "Order placed successfully"})

        # except Exception as ex:
        #     return Response({"detail": "An error has occurred", "error": str(ex)}, status=status.HTTP_400_BAD_REQUEST)


class OrderAPIView(APIView, CustomPagination):

    def get(self, request, pk=None):
        try:
            if pk:
                data = OrderSerializer(Order.objects.get(id=pk, customer__user=request.user)).data
            else:
                order_status = request.GET.get("status", None)
                if order_status:
                    order = Order.objects.filter(orderproduct__status=order_status,
                                                 customer__user=request.user).distinct()
                else:
                    order = Order.objects.filter(customer__user=request.user).order_by("-id")
                queryset = self.paginate_queryset(order, request)
                serializer = OrderSerializer(queryset, many=True).data
                data = self.get_paginated_response(serializer).data
            return Response(data)
        except (Exception,) as err:
            return Response({"detail": "An error has occurred", "error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            order = Order.objects.get(id=pk, customer__user=request.user)
            success, detail = perform_order_cancellation(order, request.user)
            if success is False:
                return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": detail})
        except Exception as ex:
            return Response({"detail": "An error has occurred", "error": str(ex)}, status=status.HTTP_400_BAD_REQUEST)


class OrderReturnView(APIView, CustomPagination):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
            To fetch all returned order by the current logged user.
        """
        try:
            returned_products = ReturnedProduct.objects.filter(returned_by=request.user).order_by("-id")
            paginated_response = self.paginate_queryset(returned_products, request)
            serialized_returned_product = ReturnedProductSerializer(instance=paginated_response, many=True,
                                                                    context={"request": request}).data
            final_serialized_response = self.get_paginated_response(serialized_returned_product).data
            return Response({"detail": final_serialized_response})
        except (Exception, ) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk=None):
        try:
            reason_id = request.data.get('reason_id', None)
            comment = request.data.get('comment', None)
            images = request.data.getlist('images', [])

            if pk is None:
                return Response({"detail": f"Order Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            if reason_id is None:
                return Response({"detail": f"Order Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            if comment is None:
                return Response({"detail": f"Your comment is needed."}, status=status.HTTP_400_BAD_REQUEST)

            # Check if images was passed into 'images' list.
            if all(images) is False:
                return Response({"detail": f"Please provide an Image"}, status=status.HTTP_400_BAD_REQUEST)

            order_product = OrderProduct.objects.filter(id=pk, status="delivered")

            if not order_product.exists():
                return Response({"detail": f"Order product does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            order_product = order_product.last()

            reason = get_object_or_404(ReturnReason, pk=reason_id)

            return_product_instance, success = ReturnedProduct.objects.get_or_create(
                returned_by=request.user, product=order_product)
            return_product_instance.reason = reason
            return_product_instance.comment = comment
            return_product_instance.save()

            for image in images:
                # Pending... waiting for image processing (waiting on the image processing method to use)
                return_product_image = ReturnProductImage(return_product=return_product_instance, image=image)
                return_product_image.save()

            # Pending... Notify admin
            return Response({"detail": f"Your report has been submitted"})
        except (Exception,) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)


class CustomerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            response = dict()

            # Wallet Information
            profile = Profile.objects.get(user=request.user)
            wallet_bal = get_wallet_info(profile)

            # Recent Orders
            recent_orders = OrderProduct.objects.filter(order__customer=profile).order_by("-id")[:10]
            serialized = OrderProductSerializer(recent_orders, many=True).data
            response['recent_orders'] = serialized
            response['wallet_information'] = wallet_bal
            # ----------------------

            # Recent Payment
            # -------------------------------

            return Response(response)

        except (Exception,) as err:
            return Response({"detail": f"{err}"}, status=status.HTTP_400_BAD_REQUEST)


class TrackOrderAPIView(APIView):

    def get(self, request):
        order_prod_id = request.GET.get("order_product_id")

        try:
            order_product = OrderProduct.objects.get(id=order_prod_id, order__customer__user=request.user)
            if order_product.tracking_id:
                # Track Order
                success, detail = perform_order_tracking(order_product)
                if success is False:
                    return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
                return Response(detail)
            else:
                return Response({"detail": "Tracking ID not found for selected order"})
        except Exception as er:
            return Response({"detail": f"{er}"}, status=status.HTTP_400_BAD_REQUEST)
