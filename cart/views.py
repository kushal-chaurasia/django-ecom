from django.conf import settings
from django.http.response import HttpResponse
from django.views.decorators import csrf
from rest_framework.views import APIView
from .models import Wishlist, CartProduct, Order, OrderItem, Offers
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from .serializers import OrderSerializer, WishlistSerializer, CartProductSerializer, UserOrderDetailSerializer
from shared.views import DropdownAPIView, PaginatedApiView
from django.db import transaction
from shared.utils import send_fcm_notification
from authentication.models import Address, User
import uuid
from django.db.models import Sum
import traceback
from django.shortcuts import render
from .utils import razorpay_payment

# Create your views here.


class WishlistView(PaginatedApiView):
    ModelClass = Wishlist
    ModelSerializerClass = WishlistSerializer
    paginated_by = 10

    def get_queryset(self, request, *args, **kwargs):
        return self.ModelClass.objects.filter(user=request.user)

    def post(self, request):
        output_data = {}
        output_detail = "Failed"
        output_status = False
        res_status = HTTP_400_BAD_REQUEST
        try:
            self.ModelClass.objects.create(
                user=request.user, product_id=request.data.get('product'))
        except Exception as e:
            output_data = str(e)
        else:
            output_detail = "Success"
            output_status = True
            res_status = HTTP_200_OK
        context = {
            "status": output_status,
            "detail": output_detail,
            "data": output_data
        }
        return Response(context, status=res_status, content_type="application/json")

    def delete(self, request, *args, **kwargs):
        output_data = {}
        output_detail = "Failed"
        output_status = False
        res_status = HTTP_400_BAD_REQUEST
        try:
            self.ModelClass.objects.filter(
                user=request.user, product_id=kwargs.get('id')).first().delete()
            output_detail = "Success"
            output_data = "Wishlist item deleted."
            output_status = True
            res_status = HTTP_200_OK
        except Exception as e:
            output_data = "Wishlist item does not exists."

        context = {
            "status": output_status,
            "detail": output_detail,
            "data": output_data
        }
        return Response(context, status=res_status, content_type="application/json")


class CartProductView(PaginatedApiView):
    ModelClass = CartProduct
    ModelSerializerClass = CartProductSerializer
    paginated_by = 10

    def get_queryset(self, request, *args, **kwargs):
        return self.ModelClass.objects.filter(user=request.user)

    def post(self, request):
        output_detail = "Failed"
        output_status = False
        res_status = HTTP_400_BAD_REQUEST
        product = int(request.data.get('product'))
        quantity = int(request.data.get('quantity')
                       ) if request.data.get('quantity') else 1
        try:
            if product:
                self.ModelClass.objects.create(
                    user=request.user, product_id=product, quantity=quantity)
                output_detail = "Success"
                output_status = True
                res_status = HTTP_200_OK
            else:
                output_detail = "Product ia required"
        except Exception as e:
            output_detail = str(e)
        context = {
            "status": output_status,
            "detail": output_detail,
        }
        return Response(context, status=res_status, content_type="application/json")

    def put(self, request):
        output_detail = "Failed"
        output_status = False
        res_status = HTTP_400_BAD_REQUEST
        id = request.data.get('id')
        try:
            cart_product_obj = self.ModelClass.objects.filter(pk=id).first()
            if cart_product_obj:
                cart_product_obj.quantity = int(request.data.get('quantity'))
                cart_product_obj.save()
                output_detail = "Success"
                output_status = True
                res_status = HTTP_200_OK
            else:
                output_detail = "Invalid cart product id"
        except Exception as e:
            output_detail = str(e)
        context = {
            "status": output_status,
            "detail": output_detail,
        }
        return Response(context, status=res_status, content_type="application/json")

    def delete(self, request, *args, **kwargs):
        output_detail = "Failed"
        output_status = False
        res_status = HTTP_400_BAD_REQUEST
        id = kwargs.get('id')
        try:
            if id:
                obj = self.ModelClass.objects.filter(pk=id)
                if obj.exists():
                    obj.delete()
                    output_detail = "Success"
                    output_status = True
                    res_status = HTTP_200_OK
                else:
                    output_detail = 'Invalid id'
            else:
                output_detail = "Id is required"
        except Exception as e:
            output_detail = str(e)
        context = {
            "status": output_status,
            "detail": output_detail,
        }
        return Response(context, status=res_status, content_type="application/json")


class OrderView(PaginatedApiView):
    ModelClass = Order
    ModelSerializerClass = OrderSerializer
    paginated_by = 10

    def get_queryset(self, request, *args, **kwargs):
        id = request.GET.get('id', None)
        if id:
            qs = self.ModelClass.objects.filter(pk=int(id), user=request.user)
        else:
            qs = self.ModelClass.objects.filter(user=request.user)
        return qs

    def create_order(self, request):
        if request.data.get('addres_id'):
            address_obj = Address.objects.filter(
                pk=int(request.data.get('addres_id')))
            if address_obj.exists():
                address_dict = address_obj.values(
                    'line_1', 'line_2', 'landmark', 'pincode', 'city', 'state').first()
        else:
            address_dict = dict(
                line_1=request.data.get('line_1'),
                line_2=request.data.get('line_2'),
                landmark=request.data.get('landmark'),
                pincode=request.data.get('pincode'),
                city=request.data.get('city'),
                state=request.data.get('state'),
            )

        order_obj = Order.objects.create(
            user=request.user,
            **address_dict,
            offer_code_id=request.data.get(
                'offer_code') if request.data.get('offer_code') else None,
            order_id=(str(uuid.uuid4())[
                      :15] + str(request.user.id)).replace('-', '').upper()
        )
        return order_obj

    def post(self, request):
        output_detail = "Failed"
        output_status = False
        res_status = HTTP_400_BAD_REQUEST
        output_data = {}
        try:
            with transaction.atomic():
                order_obj = self.create_order(request)
                order_items = request.data.get('order_items')
                for item in order_items:
                    OrderItem.objects.create(
                        order=order_obj,
                        product_id=item.get('product'),
                        quantity=item.get('quantity', 1)
                    )
                    if request.data.get('payment_method', 1) == 1:
                        CartProduct.objects.filter(user=request.user,
                                                   product_id=item.get('product')).delete()
                order_obj.payment_method = request.data.get(
                    'payment_method', 1)
                order_obj.order_booked = True
                order_obj.save()
            transaction.commit()

            payload = {
                "title": "Incoming Order",
                "body": f"You have received a new order with order id {order_obj.order_id}",
            }

            seller_id = list(User.objects.filter(
                is_seller=True).values_list('id', flat=True))
            send_fcm_notification(payload, seller_id)
            if order_obj.payment_method == 2:
                amount = int(order_obj.gross_total * 100)
                order_id = order_obj.order_id
                razorpay_order_id = razorpay_payment(amount, order_id)
                output_data.update({
                    'razorpay_merchant_key': settings.RAZOR_PAY_KEY,
                    'amount': amount,
                    'currency': 'INR',
                    'razorpay_order_id': razorpay_order_id,
                    'callback_url': f'{settings.WEBHOOK_URL}webhooks/payment/{order_id}/'
                })
            output_detail = "Success"
            output_status = True
            output_data.update(UserOrderDetailSerializer(order_obj).data)
            res_status = HTTP_200_OK

        except Exception as e:
            transaction.rollback()
            output_detail = str(e)

        context = {
            "status": output_status,
            "detail": output_detail,
            "data": output_data
        }
        return Response(context, status=res_status, content_type="application/json")


class OfferCodeView(DropdownAPIView):
    ModelClass = Offers
    serializer_fields = ['code', 'discount', 'image', 'description',
                         'term_and_conditions', 'offer_type', 'max_discount', 'min_cart_value']

    def get_queryset(self, request):
        if request.GET.get('code'):
            return self.ModelClass.objects.filter(code=request.GET.get('code'), is_active=True)
        return self.ModelClass.objects.filter(is_active=True)


class ApplyPromoCode(APIView):

    def post(self, request, *args, **kwargs):
        output_data = {}
        output_detail = "Failed"
        output_status = False
        res_status = HTTP_200_OK
        promo_code = request.data.get('promo_code')
        if promo_code:
            promo_obj = Offers.objects.filter(code=promo_code, is_active=True)
            if promo_obj.exists():
                cart_obj = CartProduct.objects.filter(user=request.user)
                if cart_obj.exists():
                    total_cart_value = cart_obj.aggregate(
                        Sum('total')).get('total__sum', 0)
                    if promo_obj.first().offer_type == 1:
                        if total_cart_value >= promo_obj.first().min_cart_value:
                            discount = promo_obj.first().discount
                            max_discount = promo_obj.first().max_discount
                            total_discount = total_cart_value * discount / 100
                            if total_discount > max_discount:
                                total_discount = max_discount
                            amount_payable = total_cart_value - total_discount
                            output_status = True
                            output_detail = "Promo code applied successfully!"
                            output_data = {
                                "discount": total_discount,
                                "cart_value": total_cart_value,
                                "amount_payable": amount_payable,
                                "promo_code_id": promo_obj.first().id
                            }
                            # res_status = HTTP_200_OK
                        else:
                            output_detail = "Minimum cart value not reached"
                    elif promo_obj.first().offer_type == 2:
                        if total_cart_value >= promo_obj.first().min_cart_value:
                            discount = promo_obj.first().discount
                            total_discount = discount
                            amount_payable = total_cart_value - total_discount
                            output_status = True
                            output_detail = "Promo code applied successfully!"
                            output_data = {
                                "discount": total_discount,
                                "cart_value": total_cart_value,
                                "amount_payable": amount_payable,
                                "promo_code_id": promo_obj.first().id
                            }
                            # res_status = HTTP_200_OK
                        else:
                            output_detail = "Minimum cart value not reached"
                else:
                    output_detail = "Cart is empty"
            else:
                output_detail = "Invalid promo code"
        else:
            output_detail = "Promo code is required"
        context = {
            "status": output_status,
            "detail": output_detail,
            "data": output_data
        }
        return Response(context, status=res_status, content_type="application/json")


class RazorpayPaymentHandler(APIView):
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        id = kwargs.get('id')
        order_obj = Order.objects.filter(order_id=id)
        razorpay_payment_id = request.data.get('razorpay_payment_id', None)
        razorpay_order_id = request.data.get('razorpay_order_id', None)
        razorpay_signature = request.data.get('razorpay_signature', None)
        if razorpay_order_id and razorpay_payment_id and razorpay_signature:
            order_obj.update(
                razorpay_payment_id=razorpay_payment_id,
                razorpay_order_id=razorpay_order_id,
                razorpay_signature=razorpay_signature,
                order_status=3,
                order_booked=True
            )
            CartProduct.objects.filter(user=order_obj.user).delete()
        else:
            order_obj.order_status = 2
        return Response({"status": "success"}, status=HTTP_200_OK)
