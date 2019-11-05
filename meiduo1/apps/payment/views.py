from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.orders.models import OrderInfo
from apps.payment.models import Payment
from meiduo1 import settings


class PayComView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=request.user,
                                          status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except:
            return JsonResponse({"code": 5555, "errmsg": "订单不存在"})

        from alipay import AliPay

        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()

        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )
        # 如果你是 Python 3的用户，使用默认的字符串即可
        subject = "测试订单"

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject=subject,
            return_url=settings.ALIPAY_RETURN_URL,
            # notify_url="https://example.com/notify"  # 可选, 不填则使用默认notify url
        )

        alipay_url = settings.ALIPAY_URL + '?' + order_string

        return JsonResponse({"code": 0, "errmsg": "ok", "alipay_url": alipay_url})


class PayStatusView(View):
    def get(self, request):
        """
        ttp://www.meiduo.site:8000/payment/status/?charset=utf-8
        &out_trade_no=2019102804011572235282000000004
        &method=alipay.trade.page.pay.return
        &total_amount=13008.00
        &sign=y3SBAvIkg8JFR2MBYIpcZXKwQkpzshhyeKPEONXJGefN1vHtaWlEZA3WlpIT6qQS8kueHh2wdTm2YGrUbIr7kIKpzhZBp7zqFItuLkSjC0rrfRfLqr1ZnUCpBuD7JEFHsd2jwlaRlLkJEPwecW2iwEQN2QwXnvooaPsoW7O%2BRoBx6IiYXuwLTOHWi5VN5%2BgwWxx7ER31OPXtLI4qldBwmPu0A8HhkMxRU9cQN%2FONauckmV5p7w%2Fk8yjvYMyI7PGPYOZmukZzPM23ieTcjddnq5Hcxd5NlY%2FPg%2Boi1jFkLi52C%2BcFk%2F2CWn3csnQP5ag%2BCefvD8yweFHaB7DwceJypw%3D%3D
        &trade_no=2019102822001449901000015729
        &auth_app_id=2016101300673506
        &version=1.0
        &app_id=2016101300673506
        &sign_type=RSA2
        &seller_id=2088102179325965
        &timestamp=2019-10-28+14%3A38%3A20
        """
        from alipay import AliPay

        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()

        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )


        data = request.GET.dict()
        # for rest_framework users

        signature = data.pop("sign")

        # verification
        success = alipay.verify(data, signature)
        trade_id = request.GET.get('trade_no')
        order_id = request.GET.get('out_trade_no')
        if success:

            Payment.objects.create(
                trade_id=trade_id,
                order_id=order_id
            )

            OrderInfo.objects.filter(order_id=order_id).update(status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])

        return render(request, 'pay_success.html',context={"order_id":order_id})
