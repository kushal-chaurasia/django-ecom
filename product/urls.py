from django.urls import path
from .views import CategoryView, ProductView, ProductSearchView, TrendingProductView, ProductFetchView


urlpatterns = [
    path('category/', CategoryView.as_view(), name='category'),
    path('category/<int:category_id>/', ProductView.as_view(), name='product'),
    path('search/<str:query>/', ProductSearchView.as_view(), name='search'),
    path('getproduct/<int:id>/', ProductFetchView.as_view(), name='search'),
    path('trending/', TrendingProductView.as_view(), name='trending'),
]
