import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rtl_to.settings')

app = Celery('rtl_to')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
