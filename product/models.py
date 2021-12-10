from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    image = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name


class CategoryProduct(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # image = models.TextField(null=True,blank= True)

    def __str__(self):
        return self.name


class Promotion(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=256, null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return self.name


class ProductSubCategory(models.Model):
    product = models.ForeignKey(
        CategoryProduct, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    gross_price = models.DecimalField(
        max_digits=7, decimal_places=2, default=0.00)
    calorie = models.CharField(max_length=200, null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    actual_price = models.DecimalField(
        max_digits=7, decimal_places=2, default=0.00)
    weight = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    promotion = models.ForeignKey(
        Promotion, on_delete=models.DO_NOTHING, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.promotion:
            self.actual_price = self.gross_price - \
                (self.gross_price * self.promotion.discount_percentage / 100)
        else:
            self.actual_price = self.gross_price
        super(ProductSubCategory, self).save(*args, **kwargs)

    def get_promotion(self):
        if self.promotion:
            return str(self.promotion.name)
        return ""

    def __str__(self):
        return f"{self.product.name} - {self.name} "
