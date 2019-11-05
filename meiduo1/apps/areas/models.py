# from django.db import models

# Create your models here.
from django.db import models

class Area(models.Model):
    """省市区"""
    name = models.CharField(max_length=20, verbose_name='名称')
    # area_set == subs
    # book.area_set.all()为找到一个书,获取书中所有英雄
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs',null=True, blank=True, verbose_name='上级行政区划')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '省市区'
        verbose_name_plural = '省市区'

    def __str__(self):
        return self.name