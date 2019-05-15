from unittest import TestCase
from unittest.mock import patch

from rabbit_context import RabbitContext, RabbitConnectionClosedError


@patch('rabbit_context.pika')
class TestRabbitContext(TestCase):

    def test_context_manager_opens_connection_and_channel(self, patch_pika):
        with RabbitContext():
            patch_pika.BlockingConnection.assert_called_once()
            patch_pika.BlockingConnection.return_value.channel.assert_called_once()

    def test_context_manager_closes_connection(self, patch_pika):
        with RabbitContext():
            pass
        patch_pika.BlockingConnection.return_value.close.assert_called_once()

    def test_attempt_to_publish_message_with_closed_connection_raises_correct_exception(self, patch_pika):
        with RabbitContext() as rabbit:
            def close_side_effect():
                rabbit._connection.is_open = False

            patch_pika.BlockingConnection.return_value.close.side_effect = close_side_effect

        with self.assertRaises(RabbitConnectionClosedError):
            rabbit.publish_message('This should raise an exception', 'text')

    def test_publish_message(self, patch_pika):
        with RabbitContext() as rabbit:
            rabbit.publish_message('Test message body', 'text')

        patch_pika.BasicProperties.assert_called_once_with(content_type='text')
        patched_basic_publish = patch_pika.BlockingConnection.return_value.channel.return_value.basic_publish
        patched_basic_publish.assert_called_once_with(exchange=rabbit._exchange,
                                                      routing_key=rabbit.queue_name,
                                                      body='Test message body',
                                                      properties=patch_pika.BasicProperties.return_value)
