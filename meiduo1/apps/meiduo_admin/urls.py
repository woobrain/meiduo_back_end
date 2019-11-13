from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from apps.meiduo_admin.views.admins import AdminView
from apps.meiduo_admin.views.images import ImageView
from apps.meiduo_admin.views.options import OptionsView
from apps.meiduo_admin.views.orders import OrderView
from apps.meiduo_admin.views.permissions import PermissionView
from apps.meiduo_admin.views.skus_biao import SkusGoodsView
from apps.meiduo_admin.views.spus import SPUGoodView
from apps.meiduo_admin.views.user_group import UserGroupView
from .views.goods_specs import GoodsSpecsView
# from apps.meiduo_admin.views.statistical import UserListView
from .views import statistical
from rest_framework.routers import DefaultRouter

urlpatterns = [
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^statistical/total_count/$', statistical.UserTotalCountView.as_view()),
    url(r'^statistical/day_increment/$', statistical.UserDayCountView.as_view()),
    url(r'^statistical/day_active/$', statistical.UsercountView.as_view()),
    url(r'^statistical/day_orders/$', statistical.UserOrderCountView.as_view()),
    url(r'^statistical/month_increment/$', statistical.UserMonthOrderCountView.as_view()),
    url(r'^statistical/goods_day_views/$', statistical.UserDayGoodsView.as_view()),
    url(r'users/', statistical.UserListView.as_view()),
    url(r'goods/simple/', GoodsSpecsView.as_view({'get': 'simple'})),
    url(r'goods/specs/simple/', OptionsView.as_view({'get': 'simple'})),
    url(r'skus/simple/', ImageView.as_view({'get': 'simple'})),
    # url(r'skus/images/', ImageView.as_view({'post': 'image'})),
    url(r'skus/categories/', SkusGoodsView.as_view({'get': 'simple'})),
    url(r'goods/(?P<pk>\d+)/specs/', SkusGoodsView.as_view({'get': 'specs'})),
    url(r'goods/brands/simple/', SPUGoodView.as_view({'get': 'simple'})),
    # url(r'goods/channel/categories/', SPUGoodView.as_view({'get': 'category_id1'})),
    url(r'goods/channel/categories/$', SPUGoodView.as_view({'get': 'category_id1'})),
    url(r'goods/channel/categories/(?P<pk>\d+)/$', SPUGoodView.as_view({'get': 'category_id2'})),
    url(r'goods/images/$', SPUGoodView.as_view({'post': 'image'})),
    url(r'permission/content_types/$', PermissionView.as_view({'get': 'content_types'})),
    url(r'permission/groups/simple/$', AdminView.as_view({'get': 'simple'})),
    url(r'permission/simple/$', UserGroupView.as_view({'get': 'simple'})),

    # 第一种url
    url(r'orders/(?P<pk>\d+)/status/', OrderView.as_view({'put': 'status'})),

]

router = DefaultRouter()
router.register('goods/specs', GoodsSpecsView, base_name='specs')
router.register('specs/options', OptionsView, base_name='options')
router.register('skus/images', ImageView, base_name='image')
router.register('skus', SkusGoodsView, base_name='skus')
router.register('goods', SPUGoodView, base_name='goods')
router.register('orders', OrderView, base_name='order')
router.register('permission/perms', PermissionView, base_name='perms')
router.register('permission/admins', AdminView, base_name='admins')
router.register('permission/groups', UserGroupView, base_name='group')
urlpatterns += router.urls
