from django.urls import path
from django.urls.conf import path
from .views import Register, AddressView, BannerView
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

urlpatterns = [
    path('register/', Register.as_view()),
    path('search/', Register.as_view()),
    path('address/', AddressView.as_view()),
    path('banner/', BannerView.as_view()),
    path('fcm/', FCMDeviceAuthorizedViewSet.as_view({'post': 'create'}), name='fcm-register-device'),
]