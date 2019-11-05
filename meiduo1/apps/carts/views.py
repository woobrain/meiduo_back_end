import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django_redis import get_redis_connection
# Create your views here.
from django.views import View
import pickle
from apps.goods.models import SKU
import base64


class CartsAddView(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            redis_con = get_redis_connection('carts')
            sku_list = redis_con.hgetall('user_%s' % user.id)
            s_members = redis_con.smembers('selected_%s' % user.id)
            data_dic = {}
            for sku,count in sku_list.items():
                data_dic[int(sku)] = {
                    'count':int(count),
                    'selected':sku in s_members
                }
            sku_ids = data_dic.keys()
            skus = SKU.objects.filter(id__in=sku_ids)
            data_list = []
            for sku in skus:
                data_list.append({
                    'id': sku.id,
                    'count': data_dic.get(sku.id).get('count'),
                    'selected': str(data_dic.get(sku.id).get('selected')),
                    'default_image_url': sku.default_image.url,
                    'name': sku.name,
                    'price': str(sku.price),
                    'amount': str(data_dic.get(sku.id).get('count') * sku.price)
                })

            context = {
                "cart_skus": data_list
            }
            return render(request, 'cart.html', context)


        else:
            carts_data = request.COOKIES.get('carts')
            if carts_data is None:
                context = {
                    "cart_skus": [{
                        "count": "",
                        "selected": "",
                        "default_image_url": "",
                        "name": "",
                        "price": "",
                        "amount": ""
                    }]
                }
                return render(request, 'cart.html', context)
            else:
                data_n = pickle.loads(base64.b64decode(carts_data))
                sku_ids = data_n.keys()
                skus = SKU.objects.filter(id__in=sku_ids)
                cart_skus = []
                for sku in skus:
                    cart_skus.append({
                        'id': sku.id,
                        'count': data_n.get(sku.id).get('count'),
                        'selected': str(data_n.get(sku.id).get('selected')),
                        'default_image_url': sku.default_image.url,
                        'name': sku.name,
                        'price': str(sku.price),
                        'amount': str(data_n.get(sku.id).get('count') * sku.price)
                    })

                context = {
                    'cart_skus': cart_skus
                }
                return render(request,'cart.html',context)

    def post(self, request):

        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        if not all([sku_id, count]):
            return JsonResponse({"code": 5555, "errmsg": "参数不全"})
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({"code": 5555, "errmsg": "商品不存在"})
        try:
            count = int(count)
        except:
            return JsonResponse({"code": 5555, "errmsg": "参数类型错误"})
        select = True
        user = request.user
        if user.is_authenticated:
            redis_con = get_redis_connection('carts')
            a_list = redis_con.hkeys('user_%s' % user.id)
            b = str(sku_id).encode()
            if b not in redis_con.hkeys('user_%s' % user.id):
                redis_con.hset('user_%s' % user.id, sku_id, count)
                redis_con.sadd('selected_%s' % user.id, sku_id)
                return JsonResponse({"code": 0, "errmsg": "ok"})
            else:
                count_new = int(redis_con.hget('user_%s' % user.id, sku_id).decode())
                count += count_new
                redis_con.hset('user_%s' % user.id, sku_id, count)
                return JsonResponse({"code": 0, "errmsg": "ok"})

        else:
            carts_data = request.COOKIES.get('carts')
            if carts_data is None:
                cookies_data = {
                    sku_id: {"count": count, "selected": select}
                }
            else:
                cookies_data = pickle.loads(base64.b64decode(carts_data))
                if sku_id in cookies_data:
                    count_new = cookies_data[sku_id]['count']

                    count += count_new

                    cookies_data[sku_id] = {"count": count, "selected": select}

                else:
                    cookies_data[sku_id] = {"count": count, "selected": select}

            s_cookies = pickle.dumps(cookies_data)
            s_base64 = base64.b64encode(s_cookies)
            response = JsonResponse({"code": 0, "errmsg": "ok"})
            response.set_cookie('carts', s_base64, 7 * 24 * 3600)
            return response

    def put(self,request):
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected')
        user = request.user

        try:
            sku = SKU.objects.get(id=sku_id)
        except:
            return JsonResponse({"code":5555,"errmsg":"参数不存在"})
        if user.is_authenticated:
            redis_con = get_redis_connection('carts')
            redis_con.hset('user_%s' % user.id,sku_id,count)
            if selected:
                redis_con.sadd('selected_%s' % user.id,sku_id)
            else:
                redis_con.srem('selected_%s' % user.id,sku_id)
            data = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price,
                'amount': sku.price * count
            }

            return JsonResponse({"code":0,"errmsg":"ok","cart_sku":data})
        else:
            carts_info = request.COOKIES.get('carts')
            if carts_info is not None:
                carts_dict = pickle.loads(base64.b64decode(carts_info))
            else:
                carts_dict = {}

            if sku_id in carts_dict:
                carts_dict[sku_id]={
                    "count":count,
                    "selected":selected
                }
            carts_list = base64.b64encode(pickle.dumps(carts_dict))
            data = {
                'id':sku_id,
                'count':count,
                'selected':selected,
                'default_image_url':sku.default_image.url,
                'name':sku.name,
                'price':sku.price,
                'amount':sku.price * count
            }

            response = JsonResponse({"code":0,"errmsg":"ok","cart_sku":data})
            response.set_cookie('carts', carts_list, max_age=7 * 24 * 3600)
            return response

    def delete(self,request):
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        user = request.user
        # 验证
        # 判断
        if user.is_authenticated:
            redis_con = get_redis_connection('carts')
            redis_con.hdel('user_%s'%user.id,sku_id)
            redis_con.srem('selected_%s'%user.id,sku_id)
            return JsonResponse({"code":0,"errmsg":"ok"})
        else:
            carts_data = request.COOKIES.get('carts')
            if carts_data:
                carts_dic = pickle.loads(base64.b64decode(carts_data))
            else:
                carts_dic={}

            if sku_id in carts_dic:
                del carts_dic[sku_id]
                cookie_carts = base64.b64encode(pickle.dumps(carts_dic))
                response = JsonResponse({"code":0,"errmsg":"ok"})
                response.set_cookie('carts',cookie_carts,max_age=7*24*3600)
                return response

class CartsSelectedView(View):
    def put(self,request):
        data_str = json.loads(request.body.decode())
        selected = data_str.get('selected')
        user = request.user
        if user.is_authenticated:
            redis_con = get_redis_connection('carts')
            skus = redis_con.hkeys('user_%s'%user.id)
            for sku in skus:
                if selected:

                    redis_con.sadd('selected_%s'%user.id,sku)
                else:

                    redis_con.srem('selected_%s'%user.id,sku)
            return JsonResponse({"code":0,"errmsg":"ok"})
        else:
            carts = request.COOKIES.get('carts')
            if carts:
                carts_dic = pickle.loads(base64.b64decode(carts))
            else:
                carts_dic = {}
            sku_ids = carts_dic.keys()
            for sku in sku_ids:
                carts_dic[sku]['selected'] = True
            a= carts_dic
            new_carts = base64.b64encode(pickle.dumps(carts_dic))
            response = JsonResponse({"code":0,"errmsg":"ok"})
            response.set_cookie('carts',new_carts,max_age=7*24*3600)
            return response

class CartSimpleView(View):
    def get(self,request):
        user = request.user
        if user.is_authenticated:
            redis_con = get_redis_connection('carts')
            carts_list = redis_con.hgetall('user_%s'%user.id)
            select_list = redis_con.smembers('selected_%s'%user.id)
            cart_skus = []
            for sku_id,count in carts_list.items():
                sku = SKU.objects.get(id=sku_id)
                cart_skus.append({
                    'id':int(sku_id),
                    'name':sku.name,
                    'count':int(count),
                    'default_image_url':sku.default_image.url
                })
        else:
            data_list = request.COOKIES.get('carts')
            datas = pickle.loads(base64.b64decode(data_list))
            cart_skus = []
            for sku_id,count_dic in datas.items():
                sku = SKU.objects.get(id=sku_id)
                cart_skus.append({
                    'id':sku_id,
                    'count':count_dic['count'],
                    'name':sku.name,
                    'default_image_url':sku.default_image.url
                })
        return JsonResponse({'code':0,'errmsg':'ok','cart_skus':cart_skus})