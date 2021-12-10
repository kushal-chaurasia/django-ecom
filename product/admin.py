from django.contrib import admin
from .models import Category, CategoryProduct, ProductSubCategory, Promotion
# Register your models here.


admin.site.register(ProductSubCategory)
admin.site.register(Category)
admin.site.register(CategoryProduct)
admin.site.register(Promotion)
