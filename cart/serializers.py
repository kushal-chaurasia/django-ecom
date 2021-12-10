from shared.serializers import CustomModelSerializer, ChoicesField, DateTimeSerializerField
from .models import Wishlist, CartProduct, Order, OrderItem
from rest_framework import serializers
from product.serializers import ProductSubCategorySerializer, ProductSerializer


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = Wishlist
        fields = ('product',)


class CartProductSerializer(serializers.ModelSerializer):
    product = ProductSubCategorySerializer()

    class Meta:
        model = CartProduct
        exclude = ('user',)


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSubCategorySerializer()

    class Meta:
        model = OrderItem
        exclude = ('order',)


class OrderSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    mobile_no = serializers.SerializerMethodField()
    order_items = serializers.SerializerMethodField()
    created_at = DateTimeSerializerField()
    updated_at = DateTimeSerializerField()
    offer_code = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'

    def get_order_items(self, obj):
        order_items = OrderItem.objects.filter(order=obj)
        if order_items.exists():
            serializer = OrderItemSerializer(order_items, many=True)
            return serializer.data
        return None

    def get_user_name(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name

    def get_mobile_no(self, obj):
        return obj.user.mobile_no

    def get_offer_code(self, obj):
        if obj.offer_code:
            return obj.offer_code.code
        return


class UserOrderDetailSerializer(CustomModelSerializer):
    status = ChoicesField(choices=Order.CURRENT_STATUS)

    class Meta:
        model = Order
        fields = ('order_id', 'created_at', 'status', 'is_accepted', 'order_booked',
                  'total', 'gross_total', 'offer_discount', 'delivery_charge', 'additional_tax')
