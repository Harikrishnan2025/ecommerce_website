from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Order, OrderItem

@receiver(pre_save, sender=Order)
def adjust_product_quantity_on_status_change(sender, instance, **kwargs):
    if not instance.pk:
        return 

    try:
        previous = Order.objects.get(pk=instance.pk)
    except Order.DoesNotExist:
        return

    if previous.status != 'Cancelled' and instance.status == 'Cancelled':
        for item in instance.items.all():
            item.product.quantity += item.quantity
            item.product.save()

    elif previous.status == 'Cancelled' and instance.status != 'Cancelled':
        for item in instance.items.all():
            if item.product.quantity < item.quantity:
                raise Exception(f"Not enough stock for {item.product.name}")
        for item in instance.items.all():
            item.product.quantity -= item.quantity
            item.product.save()