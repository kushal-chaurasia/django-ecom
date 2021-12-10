from django.db import models
from django.contrib.auth.models import AbstractUser
from product.models import CategoryProduct


class User(AbstractUser):
    GENDER = (
        ('Male', "MALE"),
        ('Female', "FEMALE")
    )
    mobile_no = models.CharField(
        unique=True, max_length=10, null=True, blank=True)
    profile_photo = models.CharField(max_length=256, null=True, blank=True)
    gender = models.TextField(choices=GENDER, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    access_token = models.CharField(max_length=256, unique=True)
    username = models.CharField(max_length=256, unique=True)
    is_seller = models.BooleanField(default=False)


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alias = models.CharField(max_length=250, null=True, blank=True)
    line_1 = models.CharField(max_length=150)
    line_2 = models.CharField(max_length=150, null=True, blank=True)
    landmark = models.CharField(max_length=150, null=True, blank=True)
    pincode = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=256)
    latitude = models.FloatField()
    longitudde = models.FloatField()

    def __str__(self):
        return f"{self.user.access_token} - {self.alias}"


class Banner(models.Model):
    banner_image = models.CharField(max_length=256)
    banner_text = models.CharField(max_length=256, null=True, blank=True)
    banner_description = models.TextField(null=True, blank=True)
    #promo_code = models.ForeignKey('product.Promotion', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.banner_text}"


class TredingProduct(models.Model):
    trending_product = models.OneToOneField(
        CategoryProduct, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.trending_product.name}"
