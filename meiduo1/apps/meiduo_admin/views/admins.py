from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Group
from apps.meiduo_admin.serializer.admins import AdminSerializer
from apps.meiduo_admin.serializer.user_group import UserGroupSerializer
from apps.user.models import User
from .statistical import UserPagination

class AdminView(ModelViewSet):

    serializer_class = AdminSerializer
    queryset = User.objects.filter(is_staff=True)
    pagination_class = UserPagination

    def simple(self,request):
        data = Group.objects.all()
        ser = UserGroupSerializer(data,many=True)

        return Response(ser.data)