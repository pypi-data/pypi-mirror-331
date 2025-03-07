import os

from dotenv import load_dotenv
from kombu import Queue, Exchange

load_dotenv()


SERVICE_NAME = os.environ["SERVICE_NAME"]
ALL_SERVICE_NAMES = os.environ.get("ALL_SERVICE_NAMES", SERVICE_NAME).split(",")
ALL_SERVICE_NAMES = [service.strip() for service in ALL_SERVICE_NAMES if service.strip()]

DIRECT_ROUTES = {}
for service in ALL_SERVICE_NAMES:
    DIRECT_ROUTES[f'events.{service}'] = {
        'queue': f'{service}_queue',
        'exchange': 'services_exchange',
        'exchange_type': 'direct',
        'routing_key': service
    }

DIRECT_QUEUE = [
    Queue(
        name=f'{SERVICE_NAME}_queue',
        exchange=Exchange('services_exchange', type='direct', durable=True),
        routing_key=SERVICE_NAME
    )
]

BROADCAST_ROUTE = {
    'events.broadcast': {
        'exchange': 'broadcast_events',
        'exchange_type': 'fanout',
        'routing_key': '',
    }
}
LOCAL_BROADCAST_QUEUE = Queue(
    name=f'{SERVICE_NAME}_broadcast',
    exchange=Exchange('broadcast_events', type='fanout', durable=True),
    routing_key=''
)

ROUTES = {**BROADCAST_ROUTE, **DIRECT_ROUTES}
QUEUES = DIRECT_QUEUE + [LOCAL_BROADCAST_QUEUE]
