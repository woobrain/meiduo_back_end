from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import SPUSpecification, SPU
from apps.meiduo_admin.serializer.goods_specs import SPUSpecificationSerializer, SPUSerializer
from .statistical import UserPagination


class GoodsSpecsView(ModelViewSet):

    pagination_class = UserPagination
    serializer_class = SPUSpecificationSerializer
    queryset = SPUSpecification.objects.all()

    def simple(self,request):
        data = SPU.objects.all()
        ser = SPUSerializer(data,many=True)
        return Response(ser.data)