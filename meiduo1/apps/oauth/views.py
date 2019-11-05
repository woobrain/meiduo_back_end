import logging

from django.http import JsonResponse
from redis.utils import pipeline

from apps.oauth import sinaweibopy3
from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from QQLoginTool.QQtool import OAuthQQ

from apps.oauth.models import OAuthQQUser
from apps.user.models import User
from django_redis import get_redis_connection

# from django_redis import get_redis_connection
logger = logging.getLogger('django')
QQ_CLIENT_ID = '101518219'

QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'

QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'


class QLoginView(View):
    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        # redirect_uri = request.GET.get('redirect_uri')
        if code == None:
            return HttpResponseBadRequest('code为空!')

        oauth = OAuthQQ(client_id=QQ_CLIENT_ID,
                        client_secret=QQ_CLIENT_SECRET,
                        redirect_uri=QQ_REDIRECT_URI,
                        state=next)
        token = oauth.get_access_token(code)

        openid = oauth.get_open_id(token)
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            return render(request, 'oauth_callback.html', context={'openid': openid})
        else:
            login(request, qquser.user)
            response = redirect(reverse('user1:index'))
            # 设置cookie
            response.set_cookie('username', qquser.user.username, max_age=24 * 3600)
            return response

    def post(self, request):

        openid = request.POST.get('openid')
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('pwd')
        sms_code = request.POST.get('sms_code')

        # 初步校验参数

        # 在数据库中比对
        # from django_redis import get_redis_connection

        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            user = User.objects.create_user(username=mobile, password=pwd, mobile=mobile)
        else:
            if not user.check_password(pwd):
                return HttpResponseBadRequest('密码错误')

        OAuthQQUser.objects.create(user_id=user.id, openid=openid)

        # OAuthQQUser.objects.update(openid=openid,user_id=user.id)
        login(request, user)

        response = redirect(reverse('user1:index'))

        response.set_cookie('username', user.username, max_age=24 * 3600)

        return response


        # return redirect(reverse('user:index1'))


class QloginUrl(View):
    def get(self,request):
        next = request.GET.get('next')
        oauth = OAuthQQ(client_id=QQ_CLIENT_ID,
                        client_secret=QQ_CLIENT_SECRET,
                        redirect_uri=QQ_REDIRECT_URI,
                        state=next)
        login_url = oauth.get_qq_url()
        return JsonResponse({
            "login_url":login_url,
            "code":0,
            "errmsg":"ok"
        })


class WloginUrl(View):
    def get(self,request):
        next = request.GET.get('next')
        client = sinaweibopy3.APIClient(app_key=settings.APP_KEY, app_secret=settings.APP_SECRET,
                                        redirect_uri=settings.REDIRECT_URL)
        login_url = client.get_authorize_url()
        return JsonResponse({
            "login_url":login_url,
            "code":0,
            "errmsg":"ok"
        })


class WLoginView(View):
    def get(self, request):
        code = request.GET.get('code')
        if code == None:
            return HttpResponseBadRequest('code为空')
        # app_key： app_key值
        # app_secret：app_secret值
        # redirect_uri ： 回调地址
        # return HttpResponse('hahahah')
        client = sinaweibopy3.APIClient(app_key=settings.APP_KEY, app_secret=settings.APP_SECRET,
                                        redirect_uri=settings.REDIRECT_URL)
        login_url = client.get_authorize_url()
        result = client.request_access_token(code)
        access_token = result.access_token
        # uid = result.uid
        try:
            w_user = OAuthQQUser.objects.get(weibotoken=access_token)
        except OAuthQQUser.DoesNotExist:
            return render(request, 'oauth_callback.html', {"openid": access_token})
        else:
            login(request, w_user.user)
            response = redirect(reverse('user1:index'))
            response.set_cookie('username', w_user.user.username, max_age=7 * 24 * 3600)
            return response

    def post(self, request):
        access_token = request.POST.get('openid')
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('pwd')
        pic_code = request.POST.get('pic_code')
        sms_code = request.POST.get('sms_code')

        if not all([access_token, mobile, pwd, pic_code, sms_code]):
            return HttpResponseBadRequest('参数不能为空')

        redis_con = get_redis_connection('code')
        code = redis_con.get('sms_%s'%mobile)
        # pl = redis_con.pipeline()
        # code = pl.get('sms_%s' % mobile)
        # image = pl.get('img_%s' % pic_code)
        if int(code) != int(sms_code):
            return HttpResponseBadRequest('您输入的手机验证码错误')
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            user = User.objects.create_user(username=mobile, password=pwd, mobile=mobile)
        else:
            if not user.check_password(pwd):
                return HttpResponseBadRequest('密码错误')
        OAuthQQUser.objects.create(weibotoken=access_token,user_id=user.id)
        login(request, user)
        response = redirect(reverse('user1:index'))
        response.set_cookie('username',user.username,max_age=7*24*3600)
        return response