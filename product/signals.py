from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
import os

from .models import ProductImage


@receiver(post_delete, sender=ProductImage)
def delete_image(sender, instance, **kwargs):
    pass
