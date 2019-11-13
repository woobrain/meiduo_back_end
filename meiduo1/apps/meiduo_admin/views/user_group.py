from django.contrib.auth.models import Group, Permission
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .statistical import UserPagination
from apps.meiduo_admin.serializer.user_group import UserGroupSerializer, GroupPerSerializer


class UserGroupView(ModelViewSet):

    serializer_class = UserGroupSerializer
    queryset = Group.objects.all()
    pagination_class = UserPagination

    def simple(self,request):
        data = Permission.objects.all()
        ser = GroupPerSerializer(data,many=True)

        return Response(ser.data)