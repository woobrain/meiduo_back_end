from rest_framework import serializers

from apps.goods.models import SPUSpecification, SPU


class SPUSpecificationSerializer(serializers.ModelSerializer):
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField()


    class Meta:
        model = SPUSpecification
        fields = '__all__'

class SPUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SPU
        fields = '__all__'