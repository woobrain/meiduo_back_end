import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo1.settings')

app = Celery(main='celery_tasks')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('celery_tasks.config', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email','celery_tasks.detail_html'])


# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))

# celery -A celery_tasks.main worker -l info
# celery -A celery_tasks.main worker -l info -P eventlet -c 1000