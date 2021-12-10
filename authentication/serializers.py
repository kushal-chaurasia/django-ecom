from django.db import models
from rest_framework import fields
from shared.serializers import CustomModelSerializer
from .models import Address, User


class AddressSerializer(CustomModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class UserSerializer(CustomModelSerializer):
    class Meta:
        model = User
        read_only_fields = ['is_seller', 'is_active', 'username']
        fields = ['username', 'first_name', 'last_name',
                  'is_seller', 'is_active', 'mobile_no', 'email', ]
