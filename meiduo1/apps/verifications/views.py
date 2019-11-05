import random

from django.http import HttpResponse
from django.http import JsonResponse
from django.views import View
from django_redis import get_redis_connection

from libs.captcha.captcha import captcha


class ImageView(View):
    def get(self, request, uuid):
        text, image = captcha.generate_captcha()

        redis_con = get_redis_connection('code')

        # redis_con.setex(key, time, value)
        redis_con.setex('img_%s' % uuid, 120, text)

        return HttpResponse(image, content_type='image/jpeg')


class CodeView(View):

    def get(self, request,mobile):
        # 1.接受参数
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        # 2.检验参数
        if not all([image_code, uuid]):
            return JsonResponse({"code":"4002","errmsg": "缺少必要参数"})

        redis_con = get_redis_connection('code')
        code = redis_con.get('img_%s' % uuid)
        mobile_flag = redis_con.get('send_flag_%s' % mobile)
        if mobile_flag:
            return JsonResponse({"code":"1","errmsg":"操作太过频繁"})

        # if code is None:
        #     return JsonResponse({"code":"4001","errmsg": "验证码失效"})

        redis_con.delete('img_%s' % uuid)
        code = code.decode()
        if image_code.lower() != code.lower():
            return JsonResponse({"code":"4001","errmsg": "验证码错误"})

        sms_code = '%06d' % random.randint(0, 999999)
        redis_con.setex('sms_%s' % mobile, 200, sms_code)
        redis_con.setex('send_flag_%s' % mobile, 200, 1)

        # CCP().send_template_sms(mobile, [sms_code, 2], 1)
        from celery_tasks.sms.tasks import sms_send
        sms_send.delay(mobile,sms_code)

        return JsonResponse({"code": 0, "errmsg": "发送信息成功"})
