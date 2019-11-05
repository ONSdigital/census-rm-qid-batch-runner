import os

import pika
from pika.spec import PERSISTENT_DELIVERY_MODE


class RabbitContext:

    def __init__(self, **kwargs):
        self._host = kwargs.get('host') or os.getenv('RABBITMQ_SERVICE_HOST', 'localhost')
        self._port = kwargs.get('port') or os.getenv('RABBITMQ_SERVICE_PORT', '6672')
        self._vhost = kwargs.get('vhost') or os.getenv('RABBITMQ_VHOST', '/')
        self._exchange = kwargs.get('exchange') or os.getenv('RABBITMQ_EXCHANGE', '')
        self._user = kwargs.get('user') or os.getenv('RABBITMQ_USER', 'guest')
        self._password = kwargs.get('password') or os.getenv('RABBITMQ_PASSWORD', 'guest')
        self.queue_name = kwargs.get('queue_name') or os.getenv('RABBITMQ_QUEUE', 'unaddressedRequestQueue')

    def __enter__(self):
        self.open_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()

    @property
    def channel(self):
        return self._channel

    def open_connection(self):
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(self._host,
                                      self._port,
                                      self._vhost,
                                      pika.PlainCredentials(self._user, self._password)))

        self._channel = self._connection.channel()
        if self.queue_name == 'localtest':
            self._channel.queue_declare(queue=self.queue_name)

        return self._connection

    def close_connection(self):
        self._connection.close()
        del self._channel
        del self._connection

    def publish_message(self, message: str, content_type: str):
        if not hasattr(self, '_connection') or not self._connection.is_open:
            raise RabbitConnectionClosedError
        self.channel.basic_publish(
            exchange=self._exchange,
            routing_key=self.queue_name,
            body=message,
            properties=pika.BasicProperties(content_type=content_type, headers=headers,
                                            delivery_mode=PERSISTENT_DELIVERY_MODE))


class RabbitConnectionClosedError(Exception):
    pass
