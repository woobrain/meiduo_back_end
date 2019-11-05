import json

from django.contrib.auth.mixins import LoginRequiredMixin

from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator
# Create your views here.
from django.utils import timezone
from django.views import View

from apps.goods.models import GoodsCategory, SKU, GoodsVisitCount
from apps.goods.utils import get_breadcrumb
from apps.user1.utils import get_categories


class ListView(View):
    def get(self, request, category_id, page_num):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return render(request, '404.html')
        sort = request.GET.get('sort', 'default')
        categories = get_categories()
        breadcrumb = get_breadcrumb(category)

        if sort == 'price':
            sort_field = 'price'
        elif sort == 'hot':
            sort_field = '-sales'
        else:
            sort = 'default'
            sort_field = 'create_time'
        skus = SKU.objects.filter(category=category, is_launched=True).order_by(sort_field)

        # data = SKU.objects.filter(category_id=category_id)

        paginator = Paginator(object_list=skus,
                              per_page=5,
                              )
        page_skus = paginator.page(page_num)

        total_page = paginator.num_pages

        context = {
            'categories': categories,  # 频道分类
            'breadcrumb': breadcrumb,  # 面包屑导航
            'sort': sort,  # 排序字段
            'category': category,  # 第三级分类
            'page_skus': page_skus,  # 分页后数据
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页码
        }

        return render(request, 'list.html', context)


class HotView(View):
    def get(self, request, category_id):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({"code": 5555, "errmsg": "ok"})
        hots = SKU.objects.filter(category=category, is_launched=True).order_by('-sales')[:2]

        hot_list = []
        for sku in hots:
            hot_list.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price

            })
        a = hot_list

        return JsonResponse({"code": 0, "errmsg": "ok", "hot_skus": hot_list})


from django import http
from django.shortcuts import render
from django.views import View
from apps.user1.utils import get_categories
from apps.goods.models import SKU, GoodsCategory

from utils.response_code import RETCODE


class DetailView(View):
    def get(self, request, sku_id):

        # 获取当前sku的信息
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')

        # 查询商品频道分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)

        # 构建当前商品的规格键
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options

        # 渲染页面
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }

        return render(request, 'detail.html', context)


class DetailVisitView(View):
    def post(self, request, category_id):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({"code": 5555, "errmsg": "error"})

        today = timezone.localdate()
        try:
            cg = GoodsVisitCount.objects.get(category=category, date=today)
        except GoodsVisitCount.DoesNotExist:
            GoodsVisitCount.objects.create(
                category=category,
                date=today,
                count=1
            )
            return JsonResponse({"code": 0, "errmsg": "ok"})
        else:
            cg.count +=1
            cg.save()
            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})


class BrowserAddView(LoginRequiredMixin,View):
    def get(self,request):
        user_id = request.user.id
        from django_redis import get_redis_connection
        redis_con = get_redis_connection('history')

        sku_ids = redis_con.lrange('his_%s' % user_id, 0, -1)

        sku_list = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            sku_list.append({
                "id":sku.id,
                "name":sku.name,
                "price":sku.price,
                "default_image_url":sku.default_image.url
            })
        return JsonResponse({"code":0,"errmsg":"ok","skus":sku_list})


    def post(self,request):
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        from django_redis import get_redis_connection
        redis_con = get_redis_connection('history')
        # # 创建Redis管道
        pl = redis_con.pipeline()
        user_id = request.user.id
        # pipeline的使用,去重操作lrem
        pl.lrem('his_%s' % user_id, 0, sku_id)
        # pipeline的使用,去重操作lpush保存
        pl.lpush('his_%s' % user_id,sku_id)
        # pipeline的使用,去重操作ltrim保存
        pl.ltrim('his_%s' % user_id,0,4)
        # # 执行请求
        pl.execute()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

