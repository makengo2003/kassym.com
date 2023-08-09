from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
import os

from .models import ProductImage


@receiver(post_delete, sender=ProductImage)
def delete_image(sender, instance, **kwargs):
    if instance.image:
        # get the path to the image file
        image_path = os.path.join(settings.MEDIA_ROOT, str(instance.image))

        # delete the image file
        if os.path.isfile(image_path):
            os.remove(image_path)
