from datetime import date, timedelta

from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.goods.models import GoodsVisitCount, GoodsCategory
from apps.meiduo_admin.serializer.model_serializer import UserSerializer
from apps.user.models import User


class UserTotalCountView(APIView):
    # 普通用户的获取
    def get(self, request):
        count = User.objects.filter(is_staff=False).count()

        return Response({
            'count': count
        })


class UserDayCountView(APIView):
    # 日增用户
    def get(self, request):
        now_day = date.today()
        count = User.objects.filter(is_staff=False, date_joined__gte=now_day).count()
        return Response({
            'count': count
        })


class UsercountView(APIView):
    # 日活用户
    def get(self, request):
        now_day = date.today()
        count = User.objects.filter(is_staff=False, last_login__gte=now_day).count()
        return Response({
            'count': count
        })


class UserOrderCountView(APIView):
    # 日下单用户---是用户
    def get(self, request):
        now_day = date.today()
        user = set(User.objects.filter(is_staff=False, orderinfo__create_time__gte=now_day))
        count = len(user)
        return Response({
            'count': count
        })


class UserMonthOrderCountView(APIView):
    # 月增用户
    def get(self, request):
        old_day = date.today() - timedelta(30)

        date_list = []
        for i in range(31):
            now_day = old_day + timedelta(i)
            next_day = old_day + timedelta(i + 1)
            count = User.objects.filter(is_staff=False, date_joined__gte=now_day, date_joined__lt=next_day).count()
            date_list.append({
                'count': count,
                'date': now_day
            })
        return Response(date_list)


class UserDayGoodsView(APIView):
    # 日分类商品访问量
    def get(self, request):
        now_day = date.today()
        goods_set = GoodsVisitCount.objects.filter(date=now_day)
        goods_list = []
        for i in goods_set:
            category = GoodsCategory.objects.get(id=i.category_id)
            goods_list.append({
                'category': category.name,
                'count': i.count
            })

        return Response(goods_list)


class UserPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'pagesize'
    max_page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'lists': data,
            'page': self.page.number,  # 当前页面
            'pages': self.page.paginator.num_pages,  # 总页数
            'pagesize': self.page_size  # 页面容量
        })


class UserListView(ListCreateAPIView):
    serializer_class = UserSerializer

    queryset = User.objects.all()
    pagination_class = UserPagination




    # def get_serializer_class(self):
    #     """
    #     此方法是对serializer_class的赋值,不指定时使用默认None
    #     :return: serializer_class
    #     """
    #
    #     if self.request.method == 'GET':
    #         return UserSerializer
    #     else:
    #         return UserAddSerializer

    # 获取查询用户
    def get_queryset(self):
        query_list = self.request.query_params
        kw = query_list.get('keyword')
        if kw == '' or kw is None:
            user = User.objects.filter(is_staff=False)
        else:
            user = User.objects.filter(username__contains=kw,is_staff=False)

        return user


# class UserAddView(ListCreateAPIView):
#
#     pagination_class = UserPagination
#
#     def get_serializer_class(self):
#         """
#         此方法是对serializer_class的赋值,不指定时使用默认None
#         :return: serializer_class
#         """
#
#         if self.request.method == 'GET':
#             return UserSerializer
#         else:
#             return UserAddSerializer
#
#     # 获取查询用户
#     def get_queryset(self):
#         query_list = self.request.query_params
#         kw = query_list.get('keyword')
#         if kw == '' or kw is None:
#             user = User.objects.all()
#         else:
#             try:
#                 user = User.objects.filter(username=kw)
#             except:
#                 user = None
#         return user
#
#
#
