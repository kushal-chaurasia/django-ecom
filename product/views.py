from .serializers import ProductSerializer, TrendingProductSerializer, FetchProductSerializer
from shared.views import PaginatedApiView, DropdownAPIView
from .models import Category, CategoryProduct
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from authentication.models import TredingProduct


# Create your views here.

class CategoryView(DropdownAPIView):
    ModelClass = Category
    serializer_fields = ['id', 'name', 'description', 'image']

    def post(self, request):
        raise MethodNotAllowed('POST')


class ProductView(PaginatedApiView):
    ModelClass = CategoryProduct
    ModelSerializerClass = ProductSerializer
    paginated_by = 10

    def get_queryset(self, request, *args, **kwargs):
        return self.ModelClass.objects.filter(category=kwargs['category_id'])


class ProductSearchView(PaginatedApiView):
    ModelClass = CategoryProduct
    ModelSerializerClass = ProductSerializer
    paginated_by = 10

    def get_queryset(self, request, *args, **kwargs):
        products = self.ModelClass.objects.filter(
            name__icontains=kwargs['query'])
        return products


class ProductFetchView(PaginatedApiView):
    ModelClass = CategoryProduct
    ModelSerializerClass = FetchProductSerializer
    paginated_by = 10

    def get_queryset(self, request, *args, **kwargs):
        products = self.ModelClass.objects.filter(id=kwargs['id'])
        return products


class TrendingProductView(PaginatedApiView):
    ModelClass = TredingProduct
    ModelSerializerClass = TrendingProductSerializer
    paginated_by = 10
