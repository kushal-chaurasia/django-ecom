from django.contrib import admin
from .models import Order, OrderItem, Offers


class OrderAdmin(admin.ModelAdmin):
    search_fields = ['order_id', ]


# Register your models here.
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Offers)
