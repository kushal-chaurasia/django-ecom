from firebase_admin.messaging import Message
from fcm_django.models import FCMDevice


def send_fcm_notification(payload: dict, user_id: list):
    device = FCMDevice.objects.filter(user_id__in=user_id)
    if device.exists():
        device.send_message(Message(data=payload))
        return True
    return False
