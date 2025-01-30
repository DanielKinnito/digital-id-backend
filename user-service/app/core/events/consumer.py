import pika
import json
from typing import Callable

class EventConsumer:
    def __init__(self, rabbitmq_url: str, queue_name: str):
        self.connection = pika.BlockingConnection(
            pika.URLParameters(rabbitmq_url)
        )
        self.channel = self.connection.channel()
        self.queue_name = queue_name
        self.channel.queue_declare(queue=queue_name)

    def consume(self, callback: Callable):
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=callback,
            auto_ack=True
        )
        print(f'Started consuming from {self.queue_name}')
        self.channel.start_consuming() 