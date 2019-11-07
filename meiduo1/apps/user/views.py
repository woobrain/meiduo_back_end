import json
import re
from datetime import datetime
from random import *

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import render, redirect

from apps.carts.utils import make_redis_cookie
from apps.goods.models import SKU
from apps.myaddr.models import Address
from apps.orders.models import OrderInfo, OrderGoods
from apps.user.models import User
from apps.user.utils import check_active_email_url
from celery_tasks.email.tasks import send_active_email
from . import models
# Create your views here.
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection


class Register(View):
    def get(self, request):

        return render(request, 'register.html')

    def post(self, request):
        # 1.功能分析
        #   .用户输入
        #   .前端form提交
        #   .后端获取数据并处理

        # 2.后端获取数据处理
        #  .request获取数据
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        pic_code = request.POST.get('pic_code')
        sms_code = request.POST.get('sms_code')
        #  .判断数据合法性

        # 1.数据不能为空
        # all([])迭代的对象为空,返回True
        # all([a,b,c])迭代对象里的元素不为空返回True
        if not all([username, password, password2, mobile, pic_code, sms_code]):
            return HttpResponseBadRequest('数据不能为空')
        # 2.用户名是否为5-20位
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseBadRequest('用户名是否为5-20位')
        # 3.密码是否为字母加数字加_-
        if not re.match(r'^[a-zA-Z0-9_-]{8,20}$', password):
            return HttpResponseBadRequest('请输入8-20位的密码')
        # 4.手机号是否为11位
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('手机号格式错误')
        # 5.密码判断
        if password != password2:
            return HttpResponseBadRequest('两次密码不一致')
        # .合法存入数据库
        # RegisterUsersmsCount().get()
        user = models.User.objects.create_user(username=username,
                                               password=password,
                                               mobile=mobile)

        # 返回合法信息
        # return redirect()
        # request.session['username'] = user.username
        # request.session['id'] = user.id

        from django.contrib.auth import login

        login(request, user)

        return redirect(reverse('user1:index'))
        #
        # return HttpResponse('您已经注册成功')


class RegisterUsernameCountView(View):
    def get(self, request, username):
        # ① 获取前端提交的数据
        # ② 查询数量
        count = models.User.objects.filter(username=username).count()
        #     数量为1: 重复
        #     数量为0: 不重复
        return JsonResponse({'count': count})


class RegisterUserPhoneCount(View):
    def get(self, request, mobile):
        count = models.User.objects.filter(mobile=mobile).count()

        return JsonResponse({"count": count})


# class RegisterUsersmsCount(View):
#
#     def get(self,request):
#         mobile = request.GET.get('mobile')
#         mobile = 'sms_%s' % mobile
#         sms_code = request.GET.get('sms_code')
#         redis_con = get_redis_connection('code')
#         mobile1 = redis_con.get(mobile).decode()
#         if sms_code != mobile1:
#             return JsonResponse({"error_code":"输入的验证码错误重新输入!"})


class LoginView(View):
    def get(self, request):

        return render(request, 'login.html')

    # 405 Method Not Allowed
    # 请求方式没有被允许,一般是未写此请求函数
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remember = request.POST.get('remembered')

        if not all([username, password]):
            # return JsonResponse({"code":"4002","errmsg":"参数不全"})
            return HttpResponseBadRequest("参数不全")
            # 2.用户名是否为5-20位
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseBadRequest('用户名是否为5-20位')
        # 3.密码是否为字母加数字加_-
        if not re.match(r'^[a-zA-Z0-9_-]{8,20}$', password):
            return HttpResponseBadRequest('请输入8-20位的密码')
        from django.contrib.auth import login, authenticate
        from django.contrib.auth.backends import ModelBackend
        # mobile = re.match(r'^1[3-9]\d{9}$',username).group()
        # username = User.objects.get(mobile=mobile).username
        user = authenticate(request,username=username, password=password)
        if user is None:
            return HttpResponseBadRequest("用户名或者密码不匹配")

        login(request, user)

        if remember:
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)
        # request.user = username

        response = redirect(reverse("user1:index"))
        response.set_cookie('username', user.username, max_age=3600 * 24)
        response = make_redis_cookie(request, user, response)
        return response


class LogoutView(View):
    def get(self, request):
        # 清理session
        logout(request)

        response = redirect(reverse('user1:index'))
        # 清理cookie
        # response.set_cookie('username',None,max_age=0)
        response.delete_cookie('username')
        return response


class FindPasswd(View):
    def get(self,request):
        return render(request,'find_password.html')
    def post(self,request):
        username = request.POST.get('username')
        pic_code = request.POST.get('pic_code')
        uuid = request.POST.get('uuid')
        if not all([username,pic_code]):
            return HttpResponseBadRequest('参数不全')
        redis_con = get_redis_connection('code')
        try:
            img_code = redis_con.get('img_%s'%uuid).decode().lower()
        except:
            return HttpResponseBadRequest('请输入图片验证码')
        if img_code != pic_code.lower():
            return HttpResponseBadRequest('图片验证码不正确')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponseBadRequest('用户名不存在')
        mobile = user.mobile

        # context = {
        #     "mobile":mobile
        # }
        response = redirect(reverse('user:findmobile2'))
        response.set_cookie('mobile',mobile,max_age=7*24*3600)
        response.set_cookie('user_id',user.id,max_age=7*24*3600)
        return response
        # return render(request,'input_mobile_verify.html',context)


class FindMobilex(View):
    def get(self,request):
        mobile = request.COOKIES.get('mobile')
        user_id = request.COOKIES.get('user_id')
        mobile2 = mobile[0:3]+"****"+mobile[7:11]
        try:
            user = User.objects.get(mobile=mobile,id=user_id)
        except User.DoesNotExist:
            return HttpResponseBadRequest('不当请求')
        response = render(request,'input_mobile_verify.html',{"mobile":mobile,"mobile2":mobile2})
        response.set_cookie('user_id', user.id, max_age=7 * 24 * 3600)
        response.set_cookie('mobile', mobile, max_age=7 * 24 * 3600)
        return response

    def post(self,request):
        mobile = request.POST.get('mobile')
        sms_code = request.POST.get('sms_code')
        if not all([mobile,sms_code]):
            return HttpResponseBadRequest('参数不全')
        redis_con = get_redis_connection('code')
        try:
            mobile_code = redis_con.get('sms_%s'%mobile).decode()
        except:
            return HttpResponseBadRequest('验证码失效')
        if sms_code != mobile_code:
            return HttpResponseBadRequest('验证码不正确')
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            return HttpResponseBadRequest('用户名不存在')
        response = redirect(reverse('user:modify_password'))
        response.set_cookie('user_id',user.id,max_age=7*24*3600)
        response.set_cookie('mobile',mobile,max_age=7*24*3600)
        # response.set_cookie('user_n',user.username,max_age=7*24*3600)
        return response


class FindMobile(View):
    def get(self,request,mobile):
        redis_con = get_redis_connection('code')
        mobile_flag = redis_con.get('send_flag_%s' % mobile)
        if mobile_flag:
            return JsonResponse({"code": "1", "errmsg": "操作太过频繁"})

        # if code is None:
        #     return JsonResponse({"code":"4001","errmsg": "验证码失效"})

        sms_code = '%06d' % randint(0, 999999)
        redis_con.setex('sms_%s' % mobile, 200, sms_code)
        redis_con.setex('send_flag_%s' % mobile, 200, 1)

        # CCP().send_template_sms(mobile, [sms_code, 2], 1)
        from celery_tasks.sms.tasks import sms_send
        sms_send.delay(mobile, sms_code)

        return JsonResponse({"code": 0, "errmsg": "发送信息成功"})

    # def post(self,request,mobile):
    #     # data = json.loads(request.body.decode())
    #     mobile = request.POST.get('mobile')
    #     return render(request,'modify_password.html')

class ModifyPwd(View):
    def get(self,request):
        return render(request,'modify_password.html')

    def post(self,request):
        mobile_c = request.COOKIES.get('mobile')
        user_id_c = request.COOKIES.get('user_id')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if not all([mobile_c,user_id_c,password,password2]):
            return HttpResponseBadRequest('参数不全或者登陆态已经失效')
        if not re.match(r'^[0-9A-Za-z]{8,20}$',password):
            return HttpResponseBadRequest('请输入8-20位的密码!!')
        if password != password2:
            return HttpResponseBadRequest('两次密码不一致')
        from django.contrib.auth import login, authenticate,get_user
        user = User.objects.get(mobile=mobile_c,id=user_id_c)
        user.password = make_password(password)
        user.save()

        login(request,user)

        response = redirect(reverse('user:modify_ok'))
        response.delete_cookie('mobile')
        response.delete_cookie('user_id')
        response.set_cookie('username',user.username,max_age=7*24*3600)
        return response


class ModifyOk(LoginRequiredMixin,View):
    def get(self,request):
        username = request.COOKIES.get('username')
        return render(request,'modify_ok.html',{"username":username})


class CenterView(LoginRequiredMixin, View):
    def get(self, request):
        # if request.user.is_authenticated:
        #     return render(request,'user_center_info.html')
        # else:
        #     return redirect(reverse('user:login'))
        context = {
            "username": request.user.username,
            "mobile": request.user.mobile,
            "email": request.user.email,
            "email_active": request.user.email_active,
        }
        return render(request, 'user_center_info.html', context=context)


class SiteView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_center_site.html')


class EmailView(LoginRequiredMixin, View):
    def put(self, request):
        body = request.body.decode()
        data = json.loads(body)

        email = data.get('email')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return JsonResponse({'code': 5006, 'errmsg': '邮箱不符合规则'})
        request.user.email = email
        request.user.save()

        from django.core.mail import send_mail
        #
        # def send_mail(subject, message, from_email, recipient_list,
        #               fail_silently=False, auth_user=None, auth_password=None,
        #               connection=None, html_message=None):
        # subject, message, from_email, recipient_list,
        # subject        主题
        # subject = '美多商场激活邮件'
        # # message,       内容
        # message = ''
        # # from_email,  谁发的
        # from_email = '欢乐玩家<15893775982@163.com>'
        # # recipient_list,  收件人列表
        # recipient_list = ['15893775982@163.com']
        #
        # html_mesage = "<a href='http://www.meiduo.site:8000/emailsactive/?token_id=1'>戳我有惊喜</a>"
        #
        # send_mail(subject=subject,
        #           message=message,
        #           from_email=from_email,
        #           recipient_list=recipient_list,
        #           html_message=html_mesage)
        send_active_email.delay(request.user.id, email)
        # ⑤ 返回相应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class Emailactive(View):
    def get(self, request):
        token_id = request.GET.get('token')
        if token_id is None:
            return HttpResponseBadRequest('激活失败')
        data = check_active_email_url(token_id)
        if data is None:
            return HttpResponseBadRequest('验证失败')
        id = data.get('id')
        email = data.get('email')

        try:
            user = User.objects.get(id=id, email=email)
        except User.DoesNotExist:
            return HttpResponseBadRequest('验证失败')
        user.email_active = True
        user.save()
        return redirect(reverse("user:center"))
        # return HttpResponse('激活成功')


class AddView(LoginRequiredMixin, View):
    def post(self, request):
        # count = request.user.addresses.count()
        # print(Address.objects.filter(user=request.user).count())
        user = request.user
        count = Address.objects.filter(user_id=request.user.id).count()
        if count > 20:
            return JsonResponse({"code": 5555, "errmsg": "最多可创建20个地址"})
        data_b = request.body.decode()
        data = json.loads(data_b)
        email = data.get('email')
        mobile = data.get('mobile')
        district_id = data.get('district_id')
        city_id = data.get('city_id')
        province_id = data.get('province_id')
        place = data.get('place')
        receiver = data.get('receiver')
        tel = data.get('tel')
        title = data.get('title')
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseBadRequest('缺少必传参数')
        # if not re.match(r'^1[3-9]\d{9}$', mobile):
        #     return JsonResponse({"code": 4007, "errmsg": "最多可创建20个地址"})
        # if tel:
        #     if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
        #         return JsonResponse({"code": 5002, "errmsg": "最多可创建20个地址"})
        # if email:
        #     if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        #         return JsonResponse({"code": 5001, "errmsg": "最多可创建20个地址"})

        try:
            addr = Address.objects.create(
                user=request.user,
                email=email,
                mobile=mobile,
                district_id=district_id,
                city_id=city_id,
                province_id=province_id,
                tel=tel,
                place=place,
                receiver=receiver,
                title=title,

            )
        except Exception as e:
            return JsonResponse({"code": 5555, "errmsg": "新增地指出错"})
        a = addr.province.name

        address = {
            "id": addr.id,
            "title": addr.title,
            "receiver": addr.receiver,
            "province": addr.province.name,
            "city": addr.city.name,
            "district": addr.district.name,
            "place": addr.place,
            "mobile": addr.mobile,
            "tel": addr.tel,
            "email": addr.email
        }

        return JsonResponse({"code": 0, "errmsg": "ok", "address": address})


class AddressView(LoginRequiredMixin, View):
    """用户收货地址"""

    def get(self, request):
        """提供收货地址界面"""
        # 获取用户地址列表
        login_user = request.user
        addresses = Address.objects.filter(user=login_user, is_deleted=False)

        address_dict_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "province_id": address.province_id,
                "city": address.city.name,
                "city_id": address.city_id,
                "district": address.district.name,
                "district_id": address.district_id,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(address_dict)

        context = {
            'default_address_id': login_user.default_address_id,
            'addresses': address_dict_list,
        }

        return render(request, 'user_center_site.html', context)


class UpdateDestroyAddressView(LoginRequiredMixin, View):
    """修改和删除地址"""

    def put(self, request, address_id):
        """修改地址"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return HttpResponseBadRequest('参数email有误')

        # 判断地址是否存在,并更新地址信息
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:

            return JsonResponse({'code': 5555, 'errmsg': '更新地址失败'})

        # 构造响应数据
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应更新地址结果
        return JsonResponse({'code': 0, 'errmsg': '更新地址成功', 'address': address_dict})

    def delete(self, request, address_id):
        """删除地址"""
        try:
            # 查询要删除的地址
            address = Address.objects.get(id=address_id)

            # 将地址逻辑删除设置为True
            address.is_deleted = True
            address.save()
        except Exception as e:

            return JsonResponse({'code': 7777, 'errmsg': '删除地址失败'})

        # 响应删除地址结果
        return JsonResponse({'code': 0, 'errmsg': '删除地址成功'})


class DefaultAddressView(LoginRequiredMixin, View):
    def put(self, request, address_id):
        try:
            # 接收参数,查询地址
            address = Address.objects.get(id=address_id)

            # 设置地址为默认地址
            request.user.default_address = address
            request.user.save()
        except Exception as e:

            return JsonResponse({'code': 5555, 'errmsg': '设置默认地址失败'})

        # 响应设置默认地址结果
        return JsonResponse({'code': 0, 'errmsg': '设置默认地址成功'})


class UpdateTitleAddressView(LoginRequiredMixin, View):
    """设置地址标题"""

    def put(self, request, address_id):
        """设置地址标题"""
        # 接收参数：地址标题
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')

        try:
            # 查询地址
            address = Address.objects.get(id=address_id)

            # 设置新的地址标题
            address.title = title
            address.save()
        except Exception as e:

            return JsonResponse({'code': 6666, 'errmsg': '设置地址标题失败'})

        # 4.响应删除地址结果
        return JsonResponse({'code': 0, 'errmsg': '设置地址标题成功'})


class PlaceOrderView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        user_id = User.objects.get(id=user.id)
        try:
            address_set = Address.objects.filter(user=user, is_deleted=False)
        except Address.DoesNotExist:
            address_set = None

        redis_con = get_redis_connection('carts')
        selected_list = redis_con.smembers('selected_%s' % user.id)
        carts_list = redis_con.hgetall('user_%s' % user.id)
        order_info = {}
        for sku_id in selected_list:
            order_info[sku_id] = int(carts_list[sku_id])
        skus = SKU.objects.filter(id__in=order_info.keys())
        total_count = 0
        total_amount = 0
        freight = 10
        for sku in skus:
            sku.count = int(carts_list[str(sku.id).encode()])
            sku.amount = sku.count * sku.price
            total_count += sku.count
            total_amount += sku.count * sku.price

        context = {
            'addresses': address_set,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight,
            'default_address_id': user_id.default_address_id

        }

        return render(request, 'place_order.html', context)


class CenterOrder(LoginRequiredMixin, View):
    def get(self, request,page_num):
        # order_id status total_amount  count price create_time freight
        # sku.name  sku.id
        # status freight user_id order_id create_time
        # order_id sku_id count price total_amount
        user = request.user

        if user.is_authenticated:
            orders = OrderInfo.objects.all().order_by('-create_time')
            content = []
            context = {}
            # page_skus = []
            utils_info = []
            for order in orders:
                goods = OrderGoods.objects.filter(order=order)

                for good in goods:
                    sku = SKU.objects.get(id=good.sku_id)

                    content.append({
                        "name": sku.name,
                        "id": sku.id,
                        "order_id": str(order.order_id),
                        "count": good.count,
                        "price": int(good.price),
                        "default_image": sku.default_image.url,
                        "singer_amount": good.count * int(good.price),

                    })
                # print(content)
                utils_info.append({
                    "freight": str(order.freight),
                    "order_id": str(order.order_id),
                    "create_time": order.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "method": OrderInfo.PAY_METHOD_CHOICES[order.pay_method - 1][1],
                    "total_amount": str(order.total_amount),
                    "status": OrderInfo.ORDER_STATUS_CHOICES[order.status - 1][1],
                    "status_id": order.status
                })
                # print(utils_info)
                # page_skus.append({
                #
                #     "freight": str(order.freight),
                #     "order_id": str(order.order_id),
                #     "create_time": order.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                #     "method": OrderInfo.PAY_METHOD_CHOICES[order.pay_method - 1][1],
                #     "total_amount": str(order.total_amount),
                #     "status": OrderInfo.ORDER_STATUS_CHOICES[order.status - 1][1],
                #     "status_id": order.status
                #
                # })
                # print(page_skus)
                context[order.order_id] = content

                # context = {
                #     "order_id": order.order_id,
                #     "create_time": order.create_time,
                #     "freight": str(order.freight),
                #     "all_info": content
                # }
                #     content[order.order_id] = {
                #         "name": sku.name,
                #         "id":sku.id,
                #         "status":order.status,
                #         "freight":str(order.freight),
                #         "create_time": order.create_time,
                #         "count":good.count,
                #         "price":str(good.price),
                #         "total_amount":str(order.total_amount)
                #     }
            paginator = Paginator(object_list=utils_info, per_page=2)
            try:
                page_skus = paginator.page(page_num)
            except:
                return HttpResponse('空页面')
            pages = paginator.num_pages
            context_all = {
                "page_num":page_num,
                "page_total":pages,
                "page_skus":page_skus,
                "utils_info": utils_info,
                "all_info": context
            }
            # for i in page_skus:
            #     print(i.order_id)
            # print(context_all)
            return render(request, 'user_center_order.html', context_all)
        else:
            return redirect(reverse('user:login'))


# 返回评价页面之前处理
class GoodsJudge(LoginRequiredMixin, View):
    def get(self, request):
        order_id = request.GET.get('order_id')
        order = OrderInfo.objects.get(order_id=order_id)
        goods = OrderGoods.objects.filter(order=order)
        content = []
        context = {}


        for good in goods:
            sku = SKU.objects.get(id=good.sku_id)
            content.append({
                "score": str(good.score),
                "comment": good.comment,
                "name": sku.name,
                "price": str(sku.price),
                "default_image": sku.default_image.url,
                "sku_id": sku.id,
                "display_score": OrderGoods.SCORE_CHOICES[good.score][1],
                "is_anonymous": str(good.is_anonymous),
                "order_id":good.order_id
            })
        context = {
            "skus": content
        }
        return render(request, 'goods_judge.html', context)

    def post(self, request):
        data = json.loads(request.body.decode())
        order_id = data.get('order_id')
        sku_id = data.get('sku_id')
        comment = data.get('comment')
        score = data.get('score')
        is_anonymous = data.get('is_anonymous')
        user = request.user

        if not all([order_id, comment, sku_id]):
            return JsonResponse({"code": 5555, "errmsg": "参数不全"})
        if len(comment) <= 5:
            return JsonResponse({"code": 5555, "errmsg": "评论内容小于五个字"})
        if user.is_authenticated:
            try:
                user = OrderInfo.objects.filter(order_id=order_id)
                order = OrderGoods.objects.filter(sku_id=sku_id, order_id=order_id).update(comment=comment,
                                                                                        is_anonymous=is_anonymous,
                                                                                        score=score)
                user.update(status=OrderInfo.ORDER_STATUS_ENUM['FINISHED'])
            except OrderGoods.DoesNotExist:
                return JsonResponse({"code": 5555, "errmsg": "评价失败"})
            return JsonResponse({"code": 0, "errmsg": "ok"})
        else:
            return JsonResponse({"code": 4101, "errmsg": "请登录"})



