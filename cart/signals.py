from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Order
from shared.utils import send_fcm_notification


@receiver(pre_save, sender=Order)
def send_fcm_notification_signal(sender, instance, **kwargs):
    """
    Send a notification to the user of an order.
    """
    try:
        previous_state = Order.objects.get(id=instance.id)
        if not previous_state.is_accepted and instance.is_accepted:
            payload = {
                'title': 'Order Accepted',
                'body': f'Your order with order id {instance.order_id} has been accepted.',
            }
        elif not previous_state.is_cancel and instance.is_cancel:
            payload = {
                'title': 'Order Cancelled',
                'body': f'Your order with order id {instance.order_id} has been cancelled.',
            }
        elif not previous_state.is_refunded and instance.is_refunded:
            payload = {
                'title': 'Order Refunded',
                'body': f'The refund of order with order id {instance.order_id} has been initiated.',
            }
        if instance.status != previous_state.status:
            if instance.status == 2:
                payload = {
                    "title": "Order Status Changed!",
                    "body": f"Your order with order id {instance.order_id} is being prepared!",
                }
            elif instance.status == 3:
                payload = {
                    "title": "Order Status Changed!",
                    "body": f"Your order with order id {instance.order_id} is Ready!",
                }
            elif instance.status == 4:
                payload = {
                    "title": "Order Status Changed!",
                    "body": f"Your order with order id {instance.order_id} is Shipped!",
                }

            elif instance.status == 5:
                payload = {
                    "title": "Order Status Changed!",
                    "body": f"Your order with order id {instance.order_id} is Delivered!",
                }

        send_fcm_notification(payload, [instance.user.id])
    except Order.DoesNotExist:
        pass

    except Exception as e:
        pass
