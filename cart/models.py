from django.db import models
from authentication.models import User
from product.models import CategoryProduct, ProductSubCategory
from decouple import config
from django.db.models import Sum
from shared.utils import send_fcm_notification
from decimal import Decimal

# Create your models here.


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(CategoryProduct, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')

        ordering = ['-id', ]

    def __str__(self):
        return self.user.username


class CartProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    total = models.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        unique_together = ('user', 'product')

    def save(self, *args, **kwargs):
        self.total = self.product.actual_price * self.quantity
        super(CartProduct, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.access_token} - {self.product.product.name} - {self.product.name}"


class Offers(models.Model):
    OFFER_TYPE = (
        (1, 'Percentage'),
        (2, 'Fixed'),
    )
    code = models.CharField(unique=True, max_length=10)
    image = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    discount = models.IntegerField()
    description = models.CharField(max_length=100)
    offer_type = models.IntegerField(choices=OFFER_TYPE)
    max_discount = models.IntegerField(blank=True, null=True)
    min_cart_value = models.IntegerField(blank=True, null=True)
    term_and_conditions = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.offer_type == 2:
            self.max_discount = self.discount
        super(Offers, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.code}"


class Order(models.Model):
    CURRENT_STATUS = (
        (1, 'New Order'),
        (2, 'Preparing'),
        (3, 'Ready'),
        (4, 'Shipped'),
        (5, 'Delivered'),
    )
    PAYMENT_METHOD = (
        (1, 'CASH ON DILEVERY'),
        (2, 'PAYTM')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order_id = models.CharField(max_length=20, unique=True)

    line_1 = models.CharField(max_length=150)
    line_2 = models.CharField(max_length=150, null=True, blank=True)
    landmark = models.CharField(max_length=150, null=True, blank=True)
    pincode = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=256, null=True, blank=True)

    status = models.IntegerField(choices=CURRENT_STATUS, default=1)
    is_accepted = models.BooleanField(default=False)
    is_refunded = models.BooleanField(default=False)
    is_cancel = models.BooleanField(default=False)
    order_booked = models.BooleanField(default=False)

    additional_tax = models.DecimalField(
        max_digits=7, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(
        max_digits=7, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    gross_total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    offer_code = models.ForeignKey(
        Offers, on_delete=models.DO_NOTHING, null=True, blank=True)
    offer_discount = models.DecimalField(
        max_digits=7, decimal_places=2, default=0.00)
    payment_method = models.IntegerField(choices=PAYMENT_METHOD, default=1)

    razorpay_signature = models.CharField(
        max_length=100, blank=True, default='')
    razorpay_order_id = models.CharField(max_length=25, blank=True, default='')
    razorpay_payment_id = models.CharField(
        max_length=25, blank=True, default='')

    ORDER_PAYMENT_STATUS = (
        (1, 'PENDING'),
        (2, 'FAILED'),
        (3, 'SUCCESS'),
        (4, 'REFUND'),
    )
    order_status = models.PositiveSmallIntegerField(
        choices=ORDER_PAYMENT_STATUS, default=1)

    def get_total(self):
        try:
            total = OrderItem.objects.filter(
                order=self).aggregate(Sum('total'))
            return total['total__sum'] if total['total__sum'] else Decimal(0.00)
        except:
            return 0.00

    def get_offer_discount(self):
        discount_value = Decimal(0.0)
        # Percentage
        if self.offer_code.offer_type == 1:
            if self.offer_code.min_cart_value:
                if self.total >= self.offer_code.min_cart_value:
                    discount_value = self.total * \
                        Decimal((self.offer_code.discount/100))
                    if discount_value > self.offer_code.max_discount:
                        discount_value = Decimal(self.offer_code.max_discount)
                return discount_value
            else:
                return self.total * Decimal((self.offer_code.discount/100))
        # Fixed
        elif self.offer_code.offer_type == 2:
            if self.offer_code.min_cart_value:
                if self.total >= self.offer_code.min_cart_value:
                    discount_value = Decimal(self.offer_code.discount)
                    if discount_value > self.offer_code.max_discount:
                        discount_value = Decimal(self.offer_code.max_discount)
            else:
                discount_value = Decimal(self.offer_code.discount)
        return Decimal(discount_value)

    def save(self, *args, **kwargs):
        self.total = self.get_total()
        self.additional_tax = self.total * \
            int(config('ADDITIONAL_TAX', default=1)) / 100
        if self.offer_code:
            self.offer_discount = self.get_offer_discount()
            self.gross_total = self.total - self.offer_discount + \
                self.additional_tax + self.delivery_charge
        else:
            self.gross_total = self.total + self.additional_tax + self.delivery_charge

        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return self.order_id

    class Meta:
        ordering = ['-id', ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    gross_weight = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total = self.product.actual_price * self.quantity
        self.gross_weight = self.product.weight * self.quantity
        super(OrderItem, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.order.order_id} - {self.product.product.name} - {self.product.name}"
