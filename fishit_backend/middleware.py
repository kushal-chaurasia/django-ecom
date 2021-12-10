from authentication.models import User
from rest_framework import HTTP_HEADER_ENCODING, authentication
from rest_framework import exceptions

class CustomAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        header = request.META.get('HTTP_AUTHORIZATION')
        if not header:
            return None
        header = header.strip('Bearer ')
        try:
            user_obj = User.objects.get(access_token = header)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Token contained no recognizable user identification')

        return (user_obj, None)
        

    
        

        


