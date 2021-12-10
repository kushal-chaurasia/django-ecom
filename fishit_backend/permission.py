from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, NotFound
from django.conf import settings

def is_valid_api_key(api_key = None, data_dict = None):
    if data_dict:
        api_key = data_dict.get('api_key', None)
    if api_key in settings.BACKEND_API_KEY:
        return True
    return False

class ValidateApiKey(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        api_key = request.data.get('api_key', request.GET.get('api_key', None))
        if not api_key:
            error_detail = "API Key is required"
            raise NotAuthenticated(detail = error_detail)
        
        if not is_valid_api_key(api_key = api_key):
            error_detail = "Invalid API Key"
            raise AuthenticationFailed(detail = error_detail)

        return True