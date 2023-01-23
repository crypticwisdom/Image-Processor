import datetime

from ecommerce.models import Cart


def remove_redundant_cart_cron():
    # This function removes cart that are not mapped to any user
    Cart.objects.filter(user__isnull=True, created_on__lt=datetime.datetime.now()).delete()
    return True

