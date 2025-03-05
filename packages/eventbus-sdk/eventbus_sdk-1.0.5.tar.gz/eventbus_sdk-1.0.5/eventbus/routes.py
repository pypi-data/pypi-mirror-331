import os

from dotenv import load_dotenv
from kombu import Queue, Exchange

load_dotenv()


SERVICE_NAME = os.environ["SERVICE_NAME"].strip()

DIRECT_ROUTES = {
    f'events.{SERVICE_NAME}': {
        'queue': f'{SERVICE_NAME}_queue',
        'exchange': 'services_exchange',
        'exchange_type': 'direct',
        'routing_key': SERVICE_NAME
    }
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
BROADCAST_QUEUE = [
    Queue(
        name=f'{SERVICE_NAME}_broadcast',
        exchange=Exchange('broadcast_events', type='fanout', durable=True),
        routing_key=''
    )
]

ROUTES = {**BROADCAST_ROUTE, **DIRECT_ROUTES}
QUEUES = DIRECT_QUEUE + BROADCAST_QUEUE
