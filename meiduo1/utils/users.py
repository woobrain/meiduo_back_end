import re

import logging
from django.contrib.auth.backends import ModelBackend, UserModel
from django.http import HttpResponse

logger = logging.getLogger('django')

from apps.user.models import User


def get_mobile_user(username):
    try:
        if re.match(r'^1[3-9]\d{9}$',username):
            user = User.objects.get(mobile=username)
        else:
            user = User.objects.get(username=username)
    except Exception as e:
        logger.error(e)
        return None
    else:
        return user

class UserMobModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 当request为空时,是后台登陆
        if request is None:
            try:
                if re.match(r'^1[3-9]\d{9}$', username):
                    user = User.objects.get(mobile=username,is_staff=True)
                else:
                    user = User.objects.get(username=username,is_staff=True)
            except User.DoesNotExist:
                user = None
            if user.check_password(password):
                return user
        else:
            user = get_mobile_user(username)
            if user is not None and user.check_password(password):
                return user
            else:
                return None
