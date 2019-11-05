import base64
from django_redis import get_redis_connection

import pickle


def make_redis_cookie(request, user, response):
    carts = request.COOKIES.get('carts')
    if carts is not None:
        carts_dict = pickle.loads(base64.b64decode(carts))
        if user.is_authenticated:
            redis_con = get_redis_connection('carts')
            new_list = redis_con.hgetall('user_%s' % user.id)
            for sku_id in carts_dict:
                if str(sku_id).encode() not in new_list:
                    redis_con.hset('user_%s' % user.id, sku_id, carts_dict[sku_id]['count'])
                else:
                    a = int(new_list[str(sku_id).encode()])
                    a += carts_dict[sku_id]['count']
                    redis_con.hset('user_%s' % user.id, sku_id, a)
                b = carts_dict[sku_id]['selected']
                if carts_dict[sku_id]['selected'] is True:
                    redis_con.sadd('selected_%s' % user.id, sku_id)
                else:
                    redis_con.srem('selected_%s' % user.id, sku_id)

            response.delete_cookie('carts')
            return response
    else:
        return response

