import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Product, ProductImage

@receiver(post_delete, sender=ProductImage)
def delete_product_image_file(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)

@receiver(post_delete, sender=Product)
def delete_all_product_images(sender, instance, **kwargs):
    for image in instance.images.all():
        if image.image and os.path.isfile(image.image.path):
            os.remove(image.image.path)
