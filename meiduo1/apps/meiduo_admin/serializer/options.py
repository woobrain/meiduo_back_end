from rest_framework import serializers

from apps.goods.models import SpecificationOption, SPUSpecification


class SpecificationOptionSerializer(serializers.ModelSerializer):
    spec = serializers.StringRelatedField(read_only=True)
    spec_id = serializers.IntegerField()

    class Meta:
        model = SpecificationOption
        fields = '__all__'


class SPUSpecificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = SPUSpecification
        fields = '__all__'