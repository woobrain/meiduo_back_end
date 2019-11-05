# from cmath import rect

from libs.yuntongxun.sms import CCP
from celery_tasks.main import app


@app.task(bind=True,default_retry_delay=10)
def sms_send(self, mobile, sms_code):
    try:
        rect = CCP().send_template_sms(mobile, [sms_code, 2], 1)
    except Exception as e:
        raise self.retry(exc=e,max_retries=3)

    if rect !=0:
        raise self.retry(exc=Exception('发送失败'),max_retries=3)
