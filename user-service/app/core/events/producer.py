import pika
import json
from typing import Any

class EventProducer:
    def __init__(self, rabbitmq_url: str):
        self.connection = pika.BlockingConnection(
            pika.URLParameters(rabbitmq_url)
        )
        self.channel = self.connection.channel()

    def publish(self, routing_key: str, event_type: str, data: Any):
        self.channel.basic_publish(
            exchange='',
            routing_key=routing_key,
            body=json.dumps(data),
            properties=pika.BasicProperties(
                content_type=event_type
            )
        ) 