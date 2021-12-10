import razorpay
from django.conf import settings

razorpay_client = razorpay.Client(auth = (
    settings.RAZOR_PAY_KEY, settings.RAZOR_PAY_VALUE
))

def razorpay_payment(amount, order_id, currency = 'INR'):
    payment_details = {
        'amount': amount,
        'currency': currency,
        'receipt': order_id,
        'payment_capture': 1,
    }
    payment_dict = razorpay_client.order.create(payment_details)
    return payment_dict.get('id')
