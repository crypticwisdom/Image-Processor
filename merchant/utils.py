from ecommerce.models import Product, ProductCategory, ProductType, ProductDetail, Brand, ProductImage, Image
from home.utils import log_request
from .models import *
from store.models import Store
from store.utils import create_or_update_store


def create_update_seller(seller, request):
    seller.phone_number = request.data.get('phone')
    seller.address = request.data.get('address')
    seller.city_id = request.data.get('city_id')
    seller.state_id = request.data.get('state_id')
    seller.country_id = request.data.get('country_id')
    seller.status = request.data.get('status')
    seller.save()

    verification, created = SellerVerification.objects.get_or_create(seller=seller)
    verification.cac_number = request.data.get('cac_number')
    verification.save()

    store, created = Store.objects.get_or_create(seller=seller)
    create_or_update_store(store, request)

    return True


def create_product(request, seller):
    data = request.data
    store = Store.objects.get(seller=seller)

    # Product Information
    name = data.get("name")
    image = data.get("image")
    cat_id = data.get("category_id")
    sub_cat_id = data.get("sub_category_id")
    prod_type_id = data.get("product_type_id")
    brand_id = data.get("brand_id")
    image_id = data.get('image_id', '')
    tag = data.get("tags", [])

    if not all([name, image, cat_id, sub_cat_id, prod_type_id, brand_id, image_id]):
        return False, "Name, image, category, sub category, brand, and product type are required fields", None

    category = ProductCategory.objects.get(id=cat_id)
    sub_category = ProductCategory.objects.get(id=sub_cat_id)
    prod_type = ProductType.objects.get(id=prod_type_id)
    brand = Brand.objects.get(id=brand_id)
    image = Image.objects.get(id=image_id)

    product, created = Product.objects.get_or_create(
        name=name, store=store, category=category, sub_category=sub_category, product_type=prod_type
    )
    product.brand = brand
    product.image = image
    product.save()
    if tag:
        tagging = ", ".join(tag)
        product.tags = tagging
        product.save()

    # Product Variants
    variant = data.get("variants", [])
    if variant:
        add_or_update_product_detail(variant, product)

    return True, "Product added successfully", product


def add_or_update_product_detail(variants, product):
    try:
        variation_list = list()
        for variation in variants:
            product_variation = None
            variation_id = variation.get('id', '')
            sku = variation.get('sku', '')
            size = variation.get('size', '')
            color = variation.get('color', '')
            discount = variation.get('discount', 0.0)
            price = variation.get('price', 0.0)
            stock = variation.get('stock', 0)
            images = variation.get('images', [])
            if variation_id:
                product_variation = ProductDetail.objects.get(pk=variation_id)
                product_variation.sku = sku
                product_variation.size = size
                product_variation.color = color
                product_variation.discount = discount
                product_variation.price = price
                product_variation.stock = stock
                product_variation.save()
            else:
                product_variation = ProductDetail.objects.create(
                    product=product, sku=sku, size=size, color=color, discount=discount, price=price, stock=stock
                )

            if product_variation.id not in variation_list:
                variation_list.append(product_variation.id)

            if product_variation:
                if images:
                    add_product_detail_images(images, product_variation)
        ProductDetail.objects.filter(product=product).exclude(id__in=variation_list).delete()

    except Exception as ex:
        log_request(f"An error occurred. Error: {ex}")


def add_product_detail_images(images, product_detail):
    try:
        ProductImage.objects.filter(product_detail=product_detail).delete()
        for image_obj in images:
            image_id = image_obj.get('id', '')
            image = Image.objects.get(pk=image_id)
            ProductImage.objects.create(product_detail=product_detail, image=image)
    except Exception as ex:
        log_request(f"An error occurred. Error: {ex}")


def update_product(request, product):
    data = request.data
    if 'name' in data:
        product.name = data.get('name', '')
    if 'status' in data:
        product.status = data.get('status', '')
    if 'category_id' in data:
        category_id = data.get('category_id', '')
        category = ProductCategory.objects.get(pk=category_id)
        product.category = category
    if 'sub_category_id' in data:
        sub_category_id = data.get('sub_category_id', '')
        sub_category = ProductCategory.objects.get(pk=sub_category_id)
        product.sub_category = sub_category
    if 'product_type_id' in data:
        product_type_id = data.get('product_type_id', '')
        product_type = ProductType.objects.get(pk=product_type_id)
        product.product_type = product_type
    if 'brand_id' in data:
        brand_id = data.get('brand_id', '')
        brand = Brand.objects.get(pk=brand_id)
        product.brand = brand
    if 'image_id' in data:
        image_id = data.get('image_id', '')
        image = Image.objects.get(pk=image_id)
        product.image = image
    if 'tags' in data:
        tags = data.get('tags', [])
        if tags:
            product.tags = ', '.join(tags)
    product.save()
    if 'variants' in data:
        variants = data.get('variants', [])
        add_or_update_product_detail(variants, product)

    return product




