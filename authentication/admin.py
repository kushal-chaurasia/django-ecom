from django.contrib import admin
from .models import User, Address, TredingProduct, Banner
from django.contrib.auth.forms import UserChangeForm
from fcm_django.models import FCMDevice
from django.contrib.auth.models import Group


class UserEditForm(UserChangeForm):
    class Meta:
        model = User

        exclude = (
            'user_permissions',
            'groups',
            'is_superuser',
            'is_staff',
            'date_joined',
        )


class CustomUserAdmin(admin.ModelAdmin):
    form = UserEditForm
    search_fields = ['username',]


# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(Banner)
admin.site.register(TredingProduct)
admin.site.unregister(Group)
admin.site.unregister(FCMDevice)
