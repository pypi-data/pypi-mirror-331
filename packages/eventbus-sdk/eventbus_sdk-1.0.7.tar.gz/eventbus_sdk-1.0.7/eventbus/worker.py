import os

from celery import Celery
from dotenv import load_dotenv

from eventbus.routes import ROUTES, QUEUES

load_dotenv()

DJANGO_PROJECT_NAME = os.environ['DJANGO_PROJECT_NAME']

RABBIT_HOST = os.environ["AWS_MQ_RABBITMQ_URL"]
RABBIT_PORT = os.getenv("AWS_MQ_RABBITMQ_PORT", "5671")
RABBIT_USER = os.getenv("AWS_MQ_RABBITMQ_USER", "guest")
RABBIT_PASS = os.getenv("AWS_MQ_RABBITMQ_PASSWORD", "guest")
BROKER_URL = f'amqps://{RABBIT_USER}:{RABBIT_PASS}@{RABBIT_HOST}:{RABBIT_PORT}'

os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{DJANGO_PROJECT_NAME}.settings")

app = Celery('eventbus', include=['eventbus.handlers'])
app.conf.update({
    'broker_url': BROKER_URL,
    'task_routes': ROUTES,
    'task_queues': QUEUES,
})

app.autodiscover_tasks(related_name='events')