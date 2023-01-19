import json
import logging

from django.db.models import Q

from ecommerce.models import ProductCategory, ProductType, Product
from home.utils import log_request
from merchant.models import Seller
from superadmin.models import AdminUser


def create_or_update_category(data, cat_id=None):
    name = data.get("name")
    parent = data.get("parent")
    image = data.get("image")
    brands = data.get("brands")

    if cat_id:
        cat_obj = ProductCategory.objects.get(id=cat_id)
        cat_obj.name = name
        cat_obj.parent_id = parent
    else:
        cat_obj, _ = ProductCategory.objects.get_or_create(name=name, parent_id=parent)

    if image:
        cat_obj.image = image

    if brands:
        cat_obj.brands.clear()
        for brand in brands:
            try:
                cat_obj.brands.add(brand)
            except Exception as ex:
                logging.exception(ex)
    cat_obj.save()

    return cat_obj


def check_permission(request):
    admin_user = AdminUser.objects.get(user=request.user)
    if not (admin_user.role.admin_type == "super_admin" or admin_user.role.admin_type == "admin"):
        return False
    return True


def perform_banner_filter(request):
    query = Q(status='active')
    if request.data.get('merchant'):
        merchant = Seller.objects.filter(id__in=json.loads(request.data.get('merchant')))
        query &= Q(store__seller__in=merchant)
    if request.data.get('category'):
        cat = ProductCategory.objects.filter(id__in=json.loads(request.data.get('category')))
        query &= Q(category__in=cat)
    if request.data.get('sub_category'):
        sub_cat = ProductCategory.objects.filter(id__in=json.loads(request.data.get('sub_category')))
        query &= Q(sub_category__in=sub_cat)
    if request.data.get('product_type'):
        prod_type = ProductType.objects.filter(id__in=json.loads(request.data.get('product_type')))
        query &= Q(product_type__in=prod_type)
    if request.data.get('min_price'):
        query &= Q(productdetail__price__gte=request.data.get('min_price'))
    if request.data.get('max_price'):
        query &= Q(productdetail__price__lte=request.data.get('max_price'))
    if request.data.get('min_discount'):
        query &= Q(productdetail__discount__gte=request.data.get('min_discount'))
    if request.data.get('max_discount'):
        query &= Q(productdetail__discount__lte=request.data.get('max_discount'))

    result = Product.objects.filter(query, store__is_active=True, store__seller__status='active').distinct()

    return result


def create_or_edit_banner_obj(data, obj, product_id=None):
    if data.get("merchant"):
        obj.merchant.clear()
        for merchant in json.loads(data.get("merchant")):
            try:
                obj.merchant.add(merchant)
            except Exception as ex:
                log_request(ex)

    if data.get("category"):
        obj.category.clear()
        for category in json.loads(data.get("category")):
            try:
                obj.category.add(category)
            except Exception as ex:
                log_request(ex)

    if data.get("sub_category"):
        obj.sub_category.clear()
        for sub_category in json.loads(data.get("sub_category")):
            try:
                obj.sub_category.add(sub_category)
            except Exception as ex:
                log_request(ex)

    if data.get("product_type"):
        obj.product_type.clear()
        for product_type in json.loads(data.get("product_type")):
            try:
                obj.product_type.add(product_type)
            except Exception as ex:
                log_request(ex)

    if not data.get("product"):
        for product in product_id:
            try:
                obj.product.add(product)
            except Exception as ex:
                log_request(ex)

    if data.get("product"):
        obj.product.clear()
        for product in json.loads(data.get("product")):
            try:
                obj.product.add(product)
            except Exception as ex:
                log_request(ex)

    obj.save()
    return True


