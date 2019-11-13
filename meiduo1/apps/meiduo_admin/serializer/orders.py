from rest_framework import serializers

from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods

class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ('name','default_image')

class OrederGoodSerializer(serializers.ModelSerializer):

    sku = SKUSerializer()

    class Meta:
        model = OrderGoods
        fields = ('count','price','sku')


class OrderSerializer(serializers.ModelSerializer):
    # 一对多时候需要many=True,即一个订单对应多个商品
    skus = OrederGoodSerializer(many=True)

    class Meta:
        model = OrderInfo
        fields = '__all__'