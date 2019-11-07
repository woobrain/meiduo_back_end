from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from .views import statistical

urlpatterns = [
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^statistical/total_count/$', statistical.UserTotalCountView.as_view()),
    url(r'^statistical/day_increment/$', statistical.UserDayCountView.as_view()),
    url(r'^statistical/day_active/$', statistical.UsercountView.as_view()),
    url(r'^statistical/day_orders/$', statistical.UserOrderCountView.as_view()),
    url(r'^statistical/month_increment/$', statistical.UserMonthOrderCountView.as_view()),
    url(r'^statistical/goods_day_views/$', statistical.UserDayGoodsView.as_view()),
    url(r'^meiduo_admin/users/', statistical.UserListView.as_view()),
    # url(r'^meiduo_admin/users/', statistical.UserAddView.as_view()),
]