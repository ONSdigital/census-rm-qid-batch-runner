import os

import pika


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
        self._open_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connection.close()

    def _open_connection(self):
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(self._host,
                                      self._port,
                                      self._vhost,
                                      pika.PlainCredentials(self._user, self._password)))
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue=self.queue_name)

    def publish_message(self, message: str, content_type: str):
        if not self._connection.is_open:
            raise RabbitConnectionClosedError
        self._channel.basic_publish(exchange=self._exchange,
                                    routing_key=self.queue_name,
                                    body=message,
                                    properties=pika.BasicProperties(content_type=content_type))


class RabbitConnectionClosedError(Exception):
    pass
