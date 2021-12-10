from shared.views import PaginatedApiView
from cart.models import Order
from cart.serializers import OrderSerializer
from rest_framework.response import Response
from shared.utils import send_fcm_notification
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST


class SellerView(PaginatedApiView):
    ModelClass = Order
    ModelSerializerClass = OrderSerializer
    paginated_by = 10

    def get_queryset(self, request, *args, **kwargs):
        filter_data = {}
        model_fields = ['is_accepted', 'is_refunded',
                        'is_cancel', 'status', 'pincode']
        order_id = request.GET.get('order_id', '')

        if request.user.is_seller:
            for f in request.GET:
                curr = request.GET.get(f, '')
                if f in model_fields and curr:
                    filter_data[f] = curr
            if filter_data:
                qs = self.ModelClass.objects.filter(**filter_data)
            elif order_id:
                qs = self.ModelClass.objects.filter(order_id=order_id)
            else:
                qs = self.ModelClass.objects.all().order_by('-created_at')
            return qs

    def post(self, request):
        output_data = {}
        output_status = False
        output_message = 'Invalid request'
        res_status = HTTP_200_OK
        order_id = request.data.get('order_id', '')
        order_status = request.data.get('order_status', '')
        if order_id and order_status:
            order = self.ModelClass.objects.filter(id=order_id).first()
            if order.exists():
                order.status = order_status
                order.save()
                output_status = True
                output_message = 'Order status updated successfully'
                res_status = HTTP_200_OK
                payload = {
                    "title": "Order Status Changed!",
                    "body": f"Your {order.id} is being prepared!",
                }
                user_id = order.user_id
                send_fcm_notification(payload, user_id)
            else:
                output_message = 'Order not found'
        else:
            output_message = 'Invalid request'
        context = {
            'status': output_status,
            'message': output_message,
            'data': output_data
        }
        return Response(context, status=res_status, content_type='application/json')
