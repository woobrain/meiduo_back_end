from django.db import transaction
from rest_framework import serializers
from rest_framework.response import Response

from apps.goods.models import SKU, GoodsCategory, SpecificationOption, SPUSpecification, SKUSpecification

class SKUSpecSerializer(serializers.ModelSerializer):
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification
        fields = ('spec_id','option_id')

class SkusGoodsSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only=True)
    spu = serializers.StringRelatedField(read_only=True)

    category_id = serializers.IntegerField()
    spu_id = serializers.IntegerField()

    specs = SKUSpecSerializer(many=True)

    class Meta:
        model = SKU
        fields = '__all__'

    def create(self, validated_data):
        specs = validated_data.get('specs')
        del validated_data['specs']
        with transaction.atomic():
            save_point = transaction.savepoint()
            try:
                sku = super().create(validated_data)
                for spec in specs:
                    SKUSpecification.objects.create(sku=sku,option_id=spec['option_id'],spec_id=spec['spec_id'])
            except:
                transaction.savepoint_rollback(save_point)
                raise serializers.ValidationError('保存失败')

            else:
                transaction.savepoint_commit(save_point)
                return sku

    def update(self, instance, validated_data):
        specs = validated_data.get('specs')
        del validated_data['specs']
        with transaction.atomic():
            save_point = transaction.savepoint()
            try:
                sku = super().update(instance, validated_data)
                for spec in specs:
                    SKUSpecification.objects.filter(sku=sku,spec_id=spec['spec_id']).update(option_id=spec['option_id'])
            except:
                transaction.savepoint_rollback(save_point)
                raise serializers.ValidationError('保存失败')

            else:
                transaction.savepoint_commit(save_point)
                return sku


class GoodsSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsCategory
        fields = '__all__'


class SpecOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpecificationOption
        fields = ('id','value')


class SPUSpecSerializer(serializers.ModelSerializer):
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField(read_only=True)
    options = SpecOptionSerializer(read_only=True,many=True)

    class Meta:
        model = SPUSpecification
        fields = '__all__'