from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from fdfs_client.client import Fdfs_client
from apps.meiduo_admin.serializer.spus import SPUGoodSerializer, BrandSerializer, CategorySerializer
from .statistical import UserPagination
from apps.goods.models import SPU, Brand, GoodsCategory


class SPUGoodView(ModelViewSet):

    serializer_class = SPUGoodSerializer
    queryset = SPU.objects.all()
    pagination_class = UserPagination

    def simple(self,request):

        brands = Brand.objects.all()
        ser = BrandSerializer(brands, many=True)
        return Response(ser.data)

    def category_id1(self,request):

        data = GoodsCategory.objects.filter(parent=None)
        ser = CategorySerializer(data,many=True)

        return Response(ser.data)

    def category_id2(self,request,pk):

        data = GoodsCategory.objects.filter(parent=pk)
        ser = CategorySerializer(data,many=True)

        return Response(ser.data)

    def image(self,request):
        data = request.data
        image = request.data.get('image')
        client = Fdfs_client('utils/fastdfs/client.conf')
        res = client.upload_by_buffer(image.read())
        if res['Status'] != 'Upload successed.':
            return Response({'error':'上传图片失败'},status=400)
        image_url = 'http://image.meiduo.site:8888/' + res['Remote file_id']
        return Response({'img_url':image_url})