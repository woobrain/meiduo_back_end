from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.meiduo_admin.serializer.orders import OrderSerializer
from apps.orders.models import OrderInfo, OrderGoods
from .statistical import UserPagination


class OrderView(ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    # queryset =
    pagination_class = UserPagination

    def get_queryset(self):
        data = self.request.query_params
        kw = data.get('keyword')
        if kw is None or kw == '':
            order = OrderInfo.objects.all()
        else:
            order = OrderInfo.objects.filter(id__contains=kw)
        return order

    def status(self,request,pk):
        try:
            sku = OrderInfo.objects.get(order_id=pk)
        except:
            return Response({'error':'订单信息错误'},status=400)

        status_id = request.data.get('status')
        sku.status = status_id
        sku.save()
        return Response({'status':status_id})

