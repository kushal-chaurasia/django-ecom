from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from fishit_backend.permission import ValidateApiKey
from .models import User, Address, Banner
from .serializers import AddressSerializer, UserSerializer
from shared.views import DropdownAPIView
from rest_framework.exceptions import MethodNotAllowed


# Create your views here.

class Register(APIView):
    permission_classes = (ValidateApiKey,)

    def post(self, request):
        output_status = False
        output_detail = "Failed"
        res_status = status.HTTP_200_OK
        output_data = {}
        try:
            obj = User.objects.create(
                mobile_no=request.data.get('mobile_no', None),
                profile_photo=request.data.get('profile_photo', None),
                email=request.data.get('email', None),
                gender=request.data.get('gender', 'Male'),
                username=request.data.get('access_token'),
                access_token=request.data.get('access_token'),
                is_seller=request.data.get('is_seller', False),
                is_active=True
            )
            output_status = True
            output_data["is_seller"] = obj.is_seller
            output_data["is_active"] = obj.is_active
            output_detail = "Success"

        except Exception as e:
            output_detail = str(e)
            obj = User.objects.filter(access_token=request.data.get(
                'access_token')).values('is_seller', 'is_active')
            output_data["is_seller"] = obj[0]['is_seller']
            output_data["is_active"] = obj[0]['is_active']
        context = {
            'status': output_status,
            'detail': output_detail,
            'data': output_data
        }
        return Response(context, status=res_status)

    def get(self, request):
        output_status = False
        output_detail = "Failed"
        output_data = {}
        res_status = status.HTTP_400_BAD_REQUEST
        user = request.user
        if user.is_authenticated:
            output_status = True
            output_detail = "User exists in database"
            output_data = UserSerializer(user).data

            res_status = status.HTTP_200_OK
        else:
            output_detail = "User does not exist in database"
            output_status = False
            res_status = status.HTTP_404_NOT_FOUND

        context = {
            'status': output_status,
            'detail': output_detail,
            'data': output_data
        }
        return Response(context, status=res_status)

    def put(self, request):
        output_status = False
        output_detail = "Failed"
        output_data = {}
        res_status = status.HTTP_400_BAD_REQUEST
        user = request.user
        if user.is_authenticated:
            try:
                serializer = UserSerializer(
                    user, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    output_status = True
                    output_detail = "Success"
                    res_status = status.HTTP_200_OK
                else:
                    output_detail = serializer.errors
            except Exception as e:
                output_detail = str(e)
        else:
            output_detail = "User not authenticated"
            res_status = status.HTTP_401_UNAUTHORIZED
        context = {
            'status': output_status,
            'detail': output_detail,
            'data': output_data
        }
        return Response(context, status=res_status, content_type="application/json")


class AddressView(DropdownAPIView):
    ModelClass = Address
    serializer_fields = ['id', 'alias', 'line_1',
                         'line_2', 'city', 'state', 'landmark', 'pincode']
    post_serializer = AddressSerializer

    def get_queryset(self, request):
        qs = Address.objects.filter(user=request.user)
        return qs

    def delete(self, request):
        output_status = False
        output_detail = "Failed"
        res_status = status.HTTP_400_BAD_REQUEST
        id = request.GET.get('id', None)
        if id and id.isnumeric():
            obj = self.ModelClass.objects.filter(pk=int(id)).first()
            if obj and obj.user == request.user:
                obj.delete()
                output_detail = 'Success'
                output_status = True
                res_status = status.HTTP_200_OK
            else:
                output_detail = 'You dont have acces to delete the address or id is invalid'
        else:
            output_detail = 'Id is required'
        context = {
            'status': output_status,
            'details': output_detail
        }
        return Response(context, status=res_status, content_type='application/json')

    def put(self, request):
        output_status = False
        output_detail = "Failed"
        res_status = status.HTTP_200_OK
        output_data = {}
        id = request.GET.get('id')
        print(request.data)
        if id and id.isnumeric():
            obj = self.ModelClass.objects.filter(
                id=int(id), user=request.user).first()

            if obj:
                serializer = self.post_serializer(
                    obj, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    output_detail = 'Succecss'
                    output_status = True
                    res_status = status.HTTP_200_OK
                else:
                    output_data = serializer.errors
            else:
                output_detail = 'Invalid id'
        else:
            output_detail = 'Id is required'
        context = {
            'status': output_status,
            'details': output_detail,
            'data': output_data
        }
        return Response(context, status=res_status, content_type="application/json")


class BannerView(DropdownAPIView):
    ModelClass = Banner
    serializer_fields = ['banner_image', 'banner_text', 'banner_dedcription']

    def post(self, request):
        raise MethodNotAllowed('POST')
