from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from apps.meiduo_admin.views.options import OptionsView
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
    url(r'goods/simple/', GoodsSpecsView.as_view({'get':'simple'})),
    url(r'goods/specs/simple/', OptionsView.as_view({'get':'simple'})),
    # url(r'^meiduo_admin/users/', statistical.UserAddView.as_view()),
]

router = DefaultRouter()
router.register('goods/specs',GoodsSpecsView , base_name='specs')
router.register('specs/options',OptionsView , base_name='options')
urlpatterns += router.urls


