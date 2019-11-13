from rest_framework import serializers

from apps.goods.models import SPU, Brand, GoodsCategory


class SPUGoodSerializer(serializers.ModelSerializer):
    brand = serializers.StringRelatedField(read_only=True)
    brand_id = serializers.IntegerField()

    category1_id = serializers.IntegerField()
    category2_id = serializers.IntegerField()
    category3_id = serializers.IntegerField()

    class Meta:
        model = SPU
        fields = '__all__'

class BrandSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsCategory
        fields = '__all__'



