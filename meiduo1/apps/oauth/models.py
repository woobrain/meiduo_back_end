from django.db import models
from utils.models import BaseModel

class OAuthQQUser(BaseModel):
    """QQ登录用户数据"""
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, verbose_name='用户')
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)
    weibotoken = models.CharField(max_length=64, verbose_name='weibotoken', db_index=True,default=0)

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name

#
# class WAuthQQUser(BaseModel):
#     """QQ登录用户数据"""
#     user = models.ForeignKey('user.User', on_delete=models.CASCADE, verbose_name='微博用户')
#     openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)
#
#     class Meta:
#         db_table = 'tb_oauth_weibo'
#         verbose_name = 'QQ登录用户数据'
#         verbose_name_plural = verbose_name