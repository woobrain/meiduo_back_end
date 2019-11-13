from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Permission,ContentType

from apps.meiduo_admin.serializer.permissions import PermissionSerializer, ContentTypeSerializer
from .statistical import UserPagination
class PermissionView(ModelViewSet):

    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()
    pagination_class = UserPagination

    def content_types(self,request):
        data = ContentType.objects.all()
        ser = ContentTypeSerializer(data,many=True)
        return Response(ser.data)