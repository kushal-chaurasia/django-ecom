"""fishit_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from cart.views import RazorpayPaymentHandler

admin.site.site_header = 'Fishit Administration' 
admin.site.index_title = 'Control Center' 
admin.site.site_title = 'Fishit Admin'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/product/', include('product.urls')),
    path('api/cart/' , include('cart.urls')),
    path('api/seller/', include('sellerside.urls')),
    path('webhooks/payment/<str:id>/', RazorpayPaymentHandler.as_view(), name='payment_webhook'),
]
