from django.db.models import Q
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.meiduo_admin.serializer.goods_specs import SPUSerializer
from apps.meiduo_admin.serializer.options import SPUSpecificationSerializer
from apps.meiduo_admin.serializer.skus_biao import SkusGoodsSerializer, GoodsSerializer, SPUSpecSerializer
from .statistical import UserPagination

from apps.goods.models import SKU, GoodsCategory, SPUSpecification, SpecificationOption, SPU


class SkusGoodsView(ModelViewSet):
    serializer_class = SkusGoodsSerializer
    pagination_class = UserPagination

    def get_queryset(self):
        # 提取keyword
        keyword = self.request.query_params.get('keyword')

        if keyword == '' or keyword is None:
            return SKU.objects.all()
        else:
            return SKU.objects.filter(name__contains=keyword)

    def simple(self, request):
        data = GoodsCategory.objects.filter(~Q(parent_id=None))
        ser = GoodsSerializer(data, many=True)
        return Response(ser.data)

    def specs(self, request, pk):
        # data = SPUSpecification.objects.filter(spu_id=pk)
        data = SPU.objects.get(id=pk)
        specs = data.specs.all()
        ser = SPUSpecSerializer(specs, many=True)
        return Response(ser.data)


