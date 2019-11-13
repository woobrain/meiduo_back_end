from rest_framework import serializers

from apps.goods.models import SKUImage, SKU
from fdfs_client.client import Fdfs_client

from celery_tasks.detail_html.tasks import get_detail_html


class SKUImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKUImage
        fields = '__all__'

    def create(self, validated_data):
        image = validated_data['image']
        sku = validated_data['sku']
        client = Fdfs_client('utils/fastdfs/client.conf')
        res = client.upload_by_buffer(image.read())
        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError('上传错误')
        img_url = res['Remote file_id']
        img = SKUImage.objects.create(sku=sku,image=img_url)
        return img

    def update(self, instance, validated_data):
        sku = validated_data['sku']
        image = validated_data['image']
        old_id = instance.id
        client = Fdfs_client('utils/fastdfs/client.conf')
        res = client.upload_by_buffer(image.read())
        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError('上传错误')
        img = res['Remote file_id']
        obj = SKUImage.objects.get(id=old_id)
        obj.sku = sku
        obj.image = img
        obj.save()
        get_detail_html.delay(sku_id=obj.sku_id)
        return obj


class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ('id','name')