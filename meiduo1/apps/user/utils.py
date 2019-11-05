
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from meiduo1 import settings


def generic_active_email_url(id, email):
    # 实例化加密对象
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)
    # 组织数据
    data = {
        "id":id,
        "email":email
    }
    # 加密数据
    serect_data = s.dumps(data)

    return 'http://www.meiduo.site:8000/emailsactive/?token=%s' % serect_data.decode()


def check_active_email_url(token_id):

    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)

    try:
        token_id = s.loads(token_id)
    except:
        return None

    return token_id
