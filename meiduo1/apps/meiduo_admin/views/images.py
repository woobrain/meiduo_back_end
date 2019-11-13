from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import SKUImage, SKU
from apps.meiduo_admin.serializer.images import SKUImageSerializer, SKUSerializer
from .statistical import UserPagination

class ImageView(ModelViewSet):

    serializer_class = SKUImageSerializer
    queryset = SKUImage.objects.all()
    pagination_class = UserPagination

    def simple(self,request):
        data = SKU.objects.all()
        ser = SKUSerializer(data,many=True)
        return Response(ser.data)
