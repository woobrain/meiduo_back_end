import re

import logging
from django.contrib.auth.backends import ModelBackend, UserModel

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

        user = get_mobile_user(username)
        if user.check_password(password) and user is not None:
            return user
