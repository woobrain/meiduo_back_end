from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from ..serializer.options import SPUSpecificationSerializer
from apps.meiduo_admin.serializer.options import SpecificationOptionSerializer
from .statistical import UserPagination
from apps.goods.models import SpecificationOption, SPUSpecification


class OptionsView(ModelViewSet):

    serializer_class = SpecificationOptionSerializer
    queryset = SpecificationOption.objects.all()
    pagination_class = UserPagination


    def simple(self,request):
        data = SPUSpecification.objects.all()
        ser = SPUSpecificationSerializer(data,many=True)
        return Response(ser.data)