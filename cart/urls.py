from django import urls
from django.urls import path
from .views import WishlistView, CartProductView, OfferCodeView, OrderView, ApplyPromoCode

urlpatterns = [
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/<int:id>/', WishlistView.as_view()),
    path('cart/', CartProductView.as_view(), name='cart'),
    path('cart/<int:id>/', CartProductView.as_view(), name='cart'),
    path('offer/', OfferCodeView.as_view(), name='offer'),
    path('order/', OrderView.as_view(), name='order'),
    path('promo-code/', ApplyPromoCode.as_view(), name='promo-code'),

]
