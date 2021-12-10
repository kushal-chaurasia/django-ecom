from .models import CategoryProduct, ProductSubCategory
from rest_framework import serializers
from authentication.models import TredingProduct
from shared.serializers import CustomModelSerializer
from cart.models import CartProduct, Wishlist


class ProductSubCategorySerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    promotion_name = serializers.CharField(source="get_promotion")
    cart_data = serializers.SerializerMethodField()

    class Meta:
        model = ProductSubCategory
        exclude = ('product',)

    def get_cart_data(self, obj):
        in_cart = False
        in_cart_val = None
        in_cart = CartProduct.objects.filter(product=obj, user=self.context.get(
            'request').user if self.context.get('request') else None).exists()
        if in_cart:
            in_cart_val = CartProduct.objects.filter(
                product=obj, user=self.context['request'].user).count()
        return {
            'in_cart': in_cart,
            'in_cart_val': in_cart_val
        }

    def get_product_name(self, obj):
        return obj.product.name


class ProductSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    wishlist = serializers.SerializerMethodField()

    class Meta:
        model = CategoryProduct
        fields = '__all__'

    def get_wishlist(self, obj):
        return Wishlist.objects.filter(product=obj, user=self.context['request'].user).exists()

    def get_products(self, obj):
        products = ProductSubCategory.objects.filter(product=obj)
        if products.exists():
            return ProductSubCategorySerializer(products[:1], many=True, context={'request': self.context['request']}).data
        return None


class FetchProductSerializer(ProductSerializer):
    def get_products(self, obj):
        products = ProductSubCategory.objects.filter(product=obj)
        if products.exists():
            return ProductSubCategorySerializer(products, many=True, context={'request': self.context['request']}).data
        return None


class CategoryProductSerializer(CustomModelSerializer):
    class Meta:
        model = CategoryProduct
        exclude = ('category',)


class TrendingProductSerializer(serializers.ModelSerializer):
    trending_product = ProductSerializer()

    class Meta:
        model = TredingProduct
        fields = ('trending_product',)
