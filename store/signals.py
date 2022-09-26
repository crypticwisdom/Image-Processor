from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from ecommerce.models import Product
from uuid import uuid4


# post signal for generating slug field for the
@receiver(post_save, sender=Product)
def create_slug(sender, instance, created, **kwargs):
    if created:
        slug = f"{instance.name.replace(' ', '-')}-{str(uuid4()).replace('-', '')[:8]}{instance.id}"
        instance.slug = slug
        instance.save()


# Incase the name of the product was changed somehow,
# this signal would take care of renaming the Product's slug field.
@receiver(pre_save, sender=Product)
def update_slug(sender, instance, **kwargs):
    if instance:
        slug = f"{instance.name.replace(' ', '-')}-{str(uuid4()).replace('-', '')[:8]}{instance.id}"
        instance.slug = slug
