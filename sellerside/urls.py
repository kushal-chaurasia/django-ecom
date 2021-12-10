from django.urls import path
from .views import SellerView

urlpatterns = [
    path('', SellerView.as_view(), name='seller'),
]
