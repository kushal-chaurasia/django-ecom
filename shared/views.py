from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.conf import settings


class DropdownAPIView(APIView):
    ModelClass = None
    ModelSerializerClass = None
    serializer_fields = []
    object_name = None
    exempt_cache = False
    post_serializer = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.ModelClass:
            raise ValueError('ModelClass field cannot be None')
        if not (self.ModelSerializerClass or self.serializer_fields):
            raise ValueError(
                'Atleast one of serializer_fields or ModelSerializerClass must be specified')

    def get_queryset(self, request, *args, **kwargs):
        return self.ModelClass.objects.all()

    def get_serializer_class(self, request, *args, **kwargs):
        return self.ModelSerializerClass

    def get_serializer_fields(self, request, *args, **kwargs):
        return self.serializer_fields

    def get_serialized_output(self, request, *args, **kwargs):
        model_obj_list = self.get_queryset(request, *args, **kwargs)
        serializer_fields = self.get_serializer_fields(
            request, *args, **kwargs)
        if serializer_fields:
            try:
                out = list(model_obj_list.values(*serializer_fields))
                return out
            except Exception as e:
                pass
        serializer_class = self.get_serializer_class(request, *args, **kwargs)
        if serializer_class:
            return serializer_class(model_obj_list, many=True, context={'request': request}).data
        return list(model_obj_list.values())

    def update_list_output(self, request, output):
        return output

    def get(self, request, *args, **kwargs):
        class_name = self.__class__.__name__
        output_status = True
        output_detail = "success"
        res_status = status.HTTP_200_OK

        output_data = cache.get(class_name)
        if output_data is None:
            output_data = self.get_serialized_output(request, *args, **kwargs)

        output = {
            'status': output_status,
            'detail': output_detail,
            'data': output_data
        }
        output = self.update_list_output(request, output)
        return Response(output, status=res_status, content_type="application/json")

    def post(self, request):
        '''
        for the use of this post method one need to use CustomModelSerializer
        '''
        output_status = False
        output_detail = 'Failed'
        output_data = {}
        res_status = status.HTTP_400_BAD_REQUEST
        extra_data = {
            'user': request.user.id
        }
        serializer = self.post_serializer(
            data=request.data, extra_data=extra_data)
        if serializer.is_valid():
            serializer.save()
            output_status = True
            output_detail = 'Success'
            res_status = status.HTTP_200_OK
        else:
            output_data = serializer.errors
        context = {
            'status': output_status,
            'detail': output_detail,
            'data': output_data
        }
        return Response(context, status=res_status)


class PaginatedApiView(APIView):
    ModelClass = None
    ModelSerializerClass = None
    paginated_by = 10

    def get_queryset(self, request, *args, **kwargs):
        return self.ModelClass.objects.all()

    def get(self, request, *args, **kwargs):
        output_status = False
        output_detail = 'Failed'
        output_data = {}
        res_status = status.HTTP_400_BAD_REQUEST
        end = False
        qs = self.get_queryset(request, *args, **kwargs)
        if qs.exists():
            page = request.GET.get('page', 1)
            try:
                page = int(page)
            except Exception as e:
                page = 1
            qs = qs[self.paginated_by * (page - 1):self.paginated_by * page]
            if qs.__len__() < self.paginated_by:
                end = True
            output_status = True
            output_detail = 'Success'
            res_status = status.HTTP_200_OK

            output_data = self.ModelSerializerClass(
                qs, many=True, context={'request': request}).data

        else:
            output_detail = 'No data found'
        context = {
            'status': output_status,
            'detail': output_detail,
            'data': output_data,
            'end': end,
            # 'nex_page' : f"{settings.WEBHOOK_URL}/{self.url}/?page={page+1}",
            # 'prev_page' : f"{settings.WEBHOOK_URL}/{self.url}/?page={page-1}"
        }
        return Response(context, status=res_status, content_type="application/json")

    def post(self, request):
        raise NotImplementedError('Post method is not implemented')
