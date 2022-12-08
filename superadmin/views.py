import datetime
from threading import Thread

from django.contrib.auth import authenticate
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from account.utils import validate_email, register_payarena_user, create_account
from ecommerce.pagination import CustomPagination
from ecommerce.serializers import *

from account.serializers import *
from ecommerce.utils import top_monthly_categories
from home.utils import get_previous_date, get_month_start_and_end_datetime, get_year_start_and_end_datetime, \
    get_week_start_and_end_datetime
from merchant.merchant_email import merchant_account_approval_email, merchant_upload_guide_email
from merchant.permissions import *
from merchant.models import Seller, BankAccount
from merchant.serializers import SellerSerializer
from merchant.utils import create_product, update_product, create_seller, update_seller
from module.apis import u_map_registration
from store.models import Store
from store.serializers import ProductCategorySerializer
from superadmin.exceptions import raise_serializer_error_msg
from superadmin.models import AdminUser, Role
from superadmin.serializers import AdminUserSerializer, CreateAdminUserSerializerIn, BannerSerializer, RoleSerializerOut
from superadmin.utils import create_or_update_category, check_permission, perform_banner_filter, \
    create_or_edit_banner_obj
from transaction.models import Transaction
from transaction.serializers import TransactionSerializer


class DashboardAPIView(APIView):
    permission_classes = []

    def get(self, request):
        # total_merchant, total_customer, total_product, sale_analysis, last_5_purchase_item, best_5_selling_product
        # best_selling_merchant_5, recent_payments
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")
        last_7_days = request.GET.get("last_7_days")
        this_month = request.GET.get("this_month")
        this_year = request.GET.get("this_year")
        this_week = request.GET.get("this_week")

        present_day = datetime.datetime.now()
        if last_7_days == "true":
            past_7_day = get_previous_date(date=present_day, delta=7)
            start_date = past_7_day
            end_date = present_day
        elif this_month == "true":
            month_start, month_end = get_month_start_and_end_datetime(present_day)
            start_date = month_start
            end_date = month_end
        elif this_year == "true":
            year_start, year_end = get_year_start_and_end_datetime(present_day)
            start_date = year_start
            end_date = year_end
        elif this_week == "true":
            week_start, week_end = get_week_start_and_end_datetime(present_day)
            start_date = week_start
            end_date = week_end
        else:
            start_date = date_from
            end_date = date_to

        data = dict()

        latest_purchased_products = OrderProduct.objects.all()[:5]
        best_selling_products = Product.objects.all().order_by("-sale_count")[:10]
        most_viewed_products = Product.objects.all().order_by("-view_count")[:10]

        if date_from and date_to:
            latest_purchased_products = OrderProduct.objects.filter(packed_on__range=(start_date, end_date))[:5]
            best_selling_products = Product.objects.filter(updated_on__range=(start_date, end_date)).order_by(
                "-sale_count")[:10]
            most_viewed_products = Product.objects.filter(updated_on__range=(start_date, end_date)).order_by(
                "-view_count")[:10]

        last_purchased = list()
        for order_product in latest_purchased_products:
            order = dict()
            order["order_id"] = order_product.id
            order["product_name"] = order_product.product_detail.product.name
            order["image"] = request.build_absolute_uri(order_product.product_detail.product.image.image.url)
            order["amount"] = order_product.total
            order["remaining_stock"] = order_product.product_detail.stock
            last_purchased.append(order)

        best_selling = list()
        for product in best_selling_products:
            prod = dict()
            prod["product_id"] = product.id
            prod["product_name"] = product.name
            if product.image:
                prod["image"] = request.build_absolute_uri(product.image.image.url)
            else:
                prod["image"] = None
            prod["store_name"] = product.store.name
            prod["category_name"] = product.category.name
            prod["sale_count"] = product.sale_count
            best_selling.append(prod)

        most_viewed = list()
        for product in most_viewed_products:
            prod = dict()
            prod["product_id"] = product.id
            prod["product_name"] = product.name
            if product.image:
                prod["image"] = request.build_absolute_uri(product.image.image.url)
            else:
                prod["image"] = None
            prod["store_name"] = product.store.name
            prod["category_name"] = product.category.name
            prod["view_count"] = product.view_count
            most_viewed.append(prod)

        data["last_purchases"] = last_purchased
        data["best_selling_products"] = best_selling
        data["most_viewed_products"] = most_viewed
        data["top_categories_for_the_month"] = top_monthly_categories(request)
        data["total_merchant"] = Seller.objects.all().count()
        data["total_customer"] = Profile.objects.all().count()
        data["total_product"] = Product.objects.all().count()

        return Response(data)


# Product Start
class ProductAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            return Response(ProductSerializer(Product.objects.get(id=pk), context={"request": request}).data)
        except Exception as err:
            return Response({"detail": "An error has occurred", "error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        merchant_id = request.data.get("seller_id")
        try:
            seller = Seller.objects.get(id=merchant_id)
            success, detail, product = create_product(request, seller)
            if success is False:
                return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
            return Response(
                {"detail": detail, "product": ProductSerializer(product, context={"request": request}).data})
        except Exception as err:
            return Response({"detail": "An error has occurred", "error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            product = Product.objects.get(id=pk)
            query = update_product(request, product)
            return Response({"detail": "Product updated successfully",
                             "product": ProductSerializer(query, context={"request": request}).data})
        except Exception as ess:
            return Response({"detail": "An error has occurred", "error": str(ess)}, status=status.HTTP_400_BAD_REQUEST)


class ProductListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['store__name', 'name']

    def get_queryset(self):
        prod_status = self.request.GET.get("status")
        queryset = Product.objects.all().order_by("-id")
        if prod_status:
            queryset = Product.objects.filter(status=prod_status).order_by("-id")
        print(queryset)
        return queryset


# Product End

# Profile Start
class ProfileListAPIView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["user__first_name", "user__last_name", "user__email", "phone_number"]

    def get_queryset(self):
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        queryset = Profile.objects.all().order_by("-id")
        if date_from and date_to:
            queryset = Profile.objects.filter(created_on__range=[date_from, date_to]).order_by("-id")
        return queryset

    def list(self, request, *args, **kwargs):
        response = super(ProfileListAPIView, self).list(request, args, kwargs)
        response.data['total_customer'] = Profile.objects.all().count()
        response.data['total_active_customer'] = Profile.objects.filter(user__is_active=True).count()
        date = get_previous_date(date=datetime.datetime.now(), delta=7)
        response.data['recent_customer'] = Profile.objects.filter(created_on__gte=date).count()
        return response


class ProfileDetailRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    lookup_field = "id"


# Profile End

# Brand Start
class BrandListAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = BrandSerializer
    queryset = Brand.objects.all().order_by("-id")
    pagination_class = CustomPagination


class BrandDetailRetrieveAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = BrandSerializer
    queryset = Brand.objects.all()
    lookup_field = "id"


# Brand End


# ProductCategory Start
class ProductCategoryListAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ProductCategorySerializer
    queryset = ProductCategory.objects.all().order_by('-id')
    pagination_class = CustomPagination

    def create(self, request, *args, **kwargs):
        data = dict()
        permission = check_permission(request)
        if permission is False:
            return Response(
                {"detail": "You do not have permission to perform this action."}, status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = ProductCategorySerializer(data=request.data)
        if not serializer.is_valid():
            data['detail'] = 'Error in data sent'
            for key, value in serializer.errors.items():
                for text in value:
                    data['detail'] = f"Error in '{key}' sent: {text}"
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        category = create_or_update_category(data=request.data)
        return Response(ProductCategorySerializer(category, context={"request": request}).data)


class ProductCategoryDetailRetrieveAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ProductCategorySerializer
    queryset = ProductCategory.objects.all()
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        permission = check_permission(request)
        if permission is False:
            return Response(
                {"detail": "You do not have permission to perform this action."}, status=status.HTTP_401_UNAUTHORIZED
            )

        cat_id = self.kwargs.get("id")
        data = dict()
        serializer = ProductCategorySerializer(data=request.data)
        if not serializer.is_valid():
            data['detail'] = 'Error in data sent'
            for key, value in serializer.errors.items():
                for text in value:
                    data['detail'] = f"Error in '{key}' sent: {text}"
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        category = create_or_update_category(data=request.data, cat_id=cat_id)
        return Response(ProductCategorySerializer(category, context={"request": request}).data)


# ProductCategory End


# Merchant
class AdminSellerAPIView(APIView, CustomPagination):
    permission_classes = [IsAdminUser]

    def get(self, request, seller_id=None):
        if seller_id:
            serializer = SellerSerializer(Seller.objects.get(id=seller_id), context={"request": request})
        else:
            status = request.GET.get("status")
            search = request.GET.get("search")
            query = Q()
            if status:
                query &= Q(status=status)
            if search:
                query &= Q(sellerdetail__company_name__icontains=search) | Q(user__last_name__icontains=search) | \
                         Q(user__first_name__icontains=search)

            result = Seller.objects.filter(query).order_by("-id")
            queryset = self.paginate_queryset(result, request)
            data = SellerSerializer(queryset, many=True, context={"request": request}).data
            serializer = self.get_paginated_response(data)
        return Response(serializer.data)

    def put(self, request, seller_id):
        try:
            success, response = update_seller(request, seller_id)
            if success is False:
                return Response({"detail": response}, status=status.HTTP_400_BAD_REQUEST)
            serializer = SellerSerializer(Seller.objects.get(id=seller_id), context={"request": request}).data
            return Response({"detail": "Merchant account updated", "data": serializer})

        except Exception as ex:
            return Response({"detail": "An error occurred while creating merchant", "error": str(ex)},
                            status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        f_name = request.data.get("first_name")
        l_name = request.data.get("last_name")
        email = request.data.get("email")
        phone_number = request.data.get("phone_number")

        try:
            # create user and profile
            if not all([email, phone_number, f_name, l_name]):
                return Response({
                    "detail": "first name, last name, email, and phone number are required fields",
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check username exist
            if User.objects.filter(email=email).exists():
                return Response({"detail": "A user with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)

            if validate_email(email) is False:
                return Response({"detail": "Invalid Email Format"}, status=status.HTTP_400_BAD_REQUEST)

            phone_number = f"+234{phone_number[-10:]}"

            # Create account on payarena Auth Engine
            password = User.objects.make_random_password()
            """
                User instance will be created on PayArena Auth Engine only when the account is approved 
            """
            # success, detail = register_payarena_user(email, phone_number, f_name, l_name, password)
            # if success is False:
            #     return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)

            success, response = create_account(email, phone_number, password, f_name, l_name)
            if success is False:
                return Response({"detail": response}, status=status.HTTP_400_BAD_REQUEST)
            user = response.user

            success, msg = create_seller(request, user, email, phone_number)
            if success is False:
                return Response({"detail": msg}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "Merchant account created"})
        except Exception as err:
            return Response({"detail": "An error occurred while creating merchant", "error": str(err)},
                            status=status.HTTP_400_BAD_REQUEST)


class UpdateMerchantStatusAPIView(APIView):
    permission_classes = [IsAdminUser & (IsAuthorizer | IsAdmin | IsSuperAdmin)]

    def put(self, request):
        seller_id = request.data.get("seller_id")
        seller_status = request.data.get("status")

        biller_code = request.data.get("biller_code")
        merchant_id = request.data.get("merchant_id")
        feel = request.data.get("FEEL")
        fep_type = request.data.get("FEP_TYPE")

        # try:
        seller = Seller.objects.get(id=seller_id)
        seller.status = seller_status

        if seller_status == "approve":
            if not all([biller_code, feel, fep_type, merchant_id]):
                return Response({"detail": "Biller Code, MerchantID, FEEL1 and FEP_TYPE are required to onboard "
                                           "merchant"}, status=status.HTTP_400_BAD_REQUEST)

            if not (fep_type == "flat" or fep_type == "rate"):
                return Response({"detail": "FEP TYPE can either be 'rate' or 'flat'"},
                                status=status.HTTP_400_BAD_REQUEST)

            seller.biller_code = biller_code
            seller.feel = feel
            seller.fep_type = fep_type
            seller.merchant_id = merchant_id
            seller.approved_by = request.user

            store_name = Store.objects.filter(seller=seller).last().name
            bank_account = BankAccount.objects.filter(seller=seller).last()

            # Update seller on UMAP
            response = u_map_registration(
                biller_id=biller_code, description=str(store_name).upper(), merchant_id=merchant_id,
                account_no=bank_account.account_number, account_name=bank_account.account_name,
                bank_code=bank_account.bank_code, fep_type=str(fep_type).upper()[0], feel=feel
            )
            print(response)
            if response["RESPONSE_CODE"] != "00":
                reason = response["RESPONSE_DESCRIPTION"]
                return Response({"detail": reason}, status=status.HTTP_400_BAD_REQUEST)

            # Send Approval Email to seller
            Thread(target=merchant_account_approval_email, args=[seller.user.email]).start()
            Thread(target=merchant_upload_guide_email, args=[seller.user.email]).start()

        seller.save()

        if seller_status == "active" or seller_status == "approve":
            Store.objects.filter(seller=seller).update(is_active=True)
        return Response({"detail": "Merchant status updated successfully"})
        # except Exception as ex:
        #     return Response({"detail": "An error has occurred", "error": str(ex)}, status=status.HTTP_400_BAD_REQUEST)


# Admin User
class AdminUserListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsSuperAdmin]
    serializer_class = AdminUserSerializer
    pagination_class = CustomPagination
    queryset = AdminUser.objects.all().order_by("-id")

    def post(self, request, *args, **kwargs):
        serializer = CreateAdminUserSerializerIn(data=request.data)
        serializer.is_valid() or raise_serializer_error_msg(errors=serializer.errors)
        data = serializer.save()
        return Response(data)


class AdminUserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsSuperAdmin]
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        seller_id = self.kwargs.get("id")
        admin_user = get_object_or_404(AdminUser, id=seller_id)
        if not request.data:
            return Response({"detail": "Nothing was updated"})

        if request.data.get('first_name'):
            admin_user.user.first_name = request.data.get('first_name')
        if request.data.get('last_name'):
            admin_user.user.last_name = request.data.get('last_name')
        if request.data.get('password'):
            admin_user.user.set_password(request.data.get('password'))
        admin_user.user.save()

        if request.data.get('role'):
            admin_user.role_id = request.data.get('role')
            admin_user.save()

        data = dict()
        data['detail'] = "Admin user updated successfully"
        data['data'] = AdminUserSerializer(admin_user).data
        return Response(data)


class AdminBannerView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = BannerSerializer
    pagination_class = CustomPagination
    queryset = Promo.objects.all().order_by("-id")

    def post(self, request, *args, **kwargs):
        name = request.data.get('title')

        if Promo.objects.filter(title=name).exists():
            return Response({"detail": "Promo with this title already exist"}, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get("price_promo") == 'true':
            if not request.data.get('min_price') or not request.data.get('max_price'):
                return Response({'detail': 'min_price and max_price filter is required'},
                                status=status.HTTP_400_BAD_REQUEST)

        if request.data.get("discount_promo") == 'true':
            if not request.data.get('min_discount') or not request.data.get('max_discount'):
                return Response({'detail': 'min_discount and max_discount filter is required'},
                                status=status.HTTP_400_BAD_REQUEST)

        result = []
        if not request.data.get("product"):
            result = perform_banner_filter(request)
            if not result:
                return Response({'detail': 'No data found'}, status=status.HTTP_400_BAD_REQUEST)

        product_id = [product.id for product in result]

        data = request.data

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"detail": "An error has occurred", "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        obj = serializer.save()
        create_or_edit_banner_obj(data, obj, product_id)

        data = {
            'detail': "Banner created successfully"
        }
        return Response(data)


class BannerDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = BannerSerializer
    queryset = Promo.objects.all()
    lookup_field = "id"

    def put(self, request, *args, **kwargs):

        pk = self.kwargs.get("id")
        if not Promo.objects.filter(id=pk).exists():
            return Response({'detail': "Invalid promo"}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        promo = Promo.objects.get(id=pk)

        if Promo.objects.filter(title=data.get('title')).exclude(id=pk).exists():
            data = {
                'success': False,
                "detail": "Promo with this title already exist"
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get("price_promo") == 'true':
            if not request.data.get('min_price') or not request.data.get('max_price'):
                return Response({'detail': 'min_price and max_price filter is required'},
                                status=status.HTTP_400_BAD_REQUEST)

        if request.data.get("discount_promo") == 'true':
            if not request.data.get('min_discount') or not request.data.get('max_discount'):
                return Response({'detail': 'min_discount and max_discount filter is required'},
                                status=status.HTTP_400_BAD_REQUEST)

        result = []
        if not request.data.get("product"):
            result = perform_banner_filter(request)
            if not result:
                return Response({'detail': 'No data found'}, status=status.HTTP_400_BAD_REQUEST)

        product_id = [product.id for product in result]

        serializer = self.serializer_class(data=request.data, instance=promo)

        if not serializer.is_valid():
            return Response(
                {'detail': 'There is an error in data sent', 'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        obj = serializer.save()

        create_or_edit_banner_obj(data, obj, product_id)
        return Response({'detail': "Banner updated successfully"})

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs.get("id")

        if not Promo.objects.filter(id=pk):
            return Response({'detail': 'Banner does not exist'}, status=status.HTTP_404_NOT_FOUND)

        Promo.objects.filter(id=pk).delete()
        return Response({'detail': 'Banner deleted successfully'}, status=status.HTTP_200_OK)


class AdminTransactionListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = TransactionSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = [
        "order__orderproduct__product_detail__product__name",
        "order__orderproduct__product_detail__product__category__name",
        "order__orderproduct__product_detail__product__store__name", "order__orderproduct__waybill_no",
        "order__customer__user__first_name", "order__customer__user__last_name"
    ]

    def get_queryset(self):
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")

        queryset = Transaction.objects.all().order_by("-id")
        if date_from and date_to:
            queryset = Transaction.objects.filter(created_on__range=[date_from, date_to])
        return queryset


class AdminTransactionRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    lookup_field = "id"


class AdminSignInAPIView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not all([email, password]):
            return Response({"detail": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=email, password=password)
        if not user:
            return Response({"detail": "Invalid login details"}, status=status.HTTP_400_BAD_REQUEST)

        if not AdminUser.objects.filter(user=user).exists():
            return Response({"detail": "You are not permitted to perform this action"},
                            status=status.HTTP_401_UNAUTHORIZED)

        data = AdminUserSerializer(AdminUser.objects.get(user=user)).data
        return Response({"detail": "Login successful",
                         "token": f"{RefreshToken.for_user(user).access_token}", "data": data})


class OrdersView(generics.ListAPIView):
    pagination_class = CustomPagination

    def get_serializer_class(self):
        param = self.kwargs.get('param', '')
        request = self.request
        if param == 'first-level' or 'filter':
            if request.GET.get("order_id"):
                return OrderProductSerializer
            return OrderSerializer
        else:
            return OrderProductSerializer

    def get_serializer_context(self):
        data = {
            'merchant_id': self.request.data.get('merchant_id'),
            'request': self.request
        }
        return data

    def get_queryset(self):
        param = self.kwargs.get('param')
        request = self.request

        if param == 'all':
            return Order.objects.filter(payment_status="success").order_by('-created_on').distinct()

        elif param == 'first-level':
            if request.GET.get("order_id"):
                order_id = request.GET.get("order_id")
                if not Order.objects.filter(id=order_id, payment_status="success").exists():
                    return OrderProduct.objects.filter(payment_status="success").order_by('-created_on')
                order = get_object_or_404(Order, id=order_id)
                return OrderProduct.objects.filter(order=order, order__payment_status="success").order_by(
                    '-created_on').distinct()

            return Order.objects.filter(payment_status="success").order_by('-created_on').distinct()

        elif param == 'filter':
            if not self.request.GET.get('date_from') or not self.request.GET.get('date_to'):
                return Order.objects.filter(payment_status="success").order_by('-created_on').distinct()

            date_from = self.request.GET.get('date_from', '')
            date_to = self.request.GET.get('date_to', '')
            return Order.objects.filter(created_on__range=[date_from, date_to], payment_status="success").order_by(
                '-created_on').distinct()

        else:
            return Order.objects.filter(orderproduct__status=param).order_by('-created_on').distinct()


class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser & (IsSuperAdmin | IsAdmin)]
    serializer_class = OrderProductSerializer
    queryset = OrderProduct.objects.all()

    def get_object(self):
        return OrderProduct.objects.get(pk=self.kwargs['order_product_id'])

    def put(self, request, order_product_id):
        order_product = get_object_or_404(OrderProduct, pk=order_product_id)

        order_status = request.data.get('status')
        order_product.status = order_status
        order_product.save()

        # Send email to shopper
        # Send email to seller

        return Response({"detail": "Order updated successfully"})


class AdminRoleListAPIView(generics.ListAPIView):
    permission_classes = [IsSuperAdmin]
    queryset = Role.objects.all().order_by("-created_on")
    serializer_class = RoleSerializerOut



