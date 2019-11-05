from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
# 此时的是明文存储,所以比较不安全,这种方法不可行
# class User(models.Model):
#     username = models.CharField(max_length=20)
#     password = models.CharField(max_length=20)
#     mobile = models.CharField(max_length=20)

class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False,verbose_name='邮箱')
    default_address = models.ForeignKey('myaddr.Address', related_name='users', null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name='默认地址')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
