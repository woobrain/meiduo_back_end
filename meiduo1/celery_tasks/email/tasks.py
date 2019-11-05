from django.core.mail import send_mail

from apps.user.utils import generic_active_email_url
from celery_tasks.main import app


@app.task
def send_active_email(user_id,email):
    # subject, message, from_email, recipient_list,
    # subject        主题
    subject = '美多商场激活邮件'
    # message,       内容
    message = ''
    # from_email,  谁发的
    from_email = '美多商场<15893775982@163.com>'
    # recipient_list,  收件人列表
    recipient_list = [email]

    # 对用户信息进行加密
    active_url = generic_active_email_url(user_id, email)

    # 用户点击这个连接,让他跳转到指定页面,同时修改这个用户的邮件状态
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (email, active_url, active_url)

    send_mail(subject=subject,
              message=message,
              from_email=from_email,
              recipient_list=recipient_list,
              html_message=html_message)
