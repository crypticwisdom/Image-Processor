import logging

from ecommerce.models import ProductCategory


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

