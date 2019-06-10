import csv
import functools
import os
import uuid
from contextlib import contextmanager
from pathlib import Path

import pika

from generate_print_files import PRINT_FILE_TEMPLATE, generate_print_files_from_config_file_path
from generate_qid_batch import generate_messages_from_config_file_path


def generate_test_qid_batch(batch_id):
    generate_messages_from_config_file_path(
        Path(__file__).parent.resolve().joinpath('acceptance_test_batch.csv'),
        batch_id)


def wait_for_uacs_to_be_created(connection, channel, timeout=30, expected_quantity=30):
    def message_callback(channel, method, *_):
        nonlocal uac_message_count
        uac_message_count += 1
        channel.basic_ack(delivery_tag=method.delivery_tag)
        if uac_message_count >= expected_quantity:
            channel.stop_consuming()

    def _timeout_callback():
        assert False, 'Timed out waiting for messages'

    uac_message_count = 0
    connection.call_later(timeout, functools.partial(_timeout_callback, connection))
    channel.basic_consume(queue='acceptance_tests_uac', on_message_callback=message_callback)
    channel.start_consuming()


@contextmanager
def rabbit_connection_and_channel():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(os.getenv('RABBITMQ_SERVICE_HOST', 'localhost'),
                                  int(os.getenv('RABBITMQ_SERVICE_PORT', '6672')),
                                  os.getenv('RABBITMQ_VHOST', '/'),
                                  pika.PlainCredentials(os.getenv('RABBITMQ_USER', 'guest'),
                                                        os.getenv('RABBITMQ_PASSWORD', 'guest'))))
    channel = connection.channel()
    channel.exchange_declare(exchange='events', exchange_type='topic', durable=True)
    channel.queue_declare('acceptance_tests_uac', exclusive=True)
    channel.queue_bind(exchange='events', queue='acceptance_tests_uac', routing_key='event.uac.*')
    yield connection, channel
    channel.queue_delete(queue='acceptance_tests_uac')
    connection.close()


def validate_print_file_data(file_paths):
    manifests = [file_path for file_path in file_paths if file_path.suffix == '.manifest']
    print_files = [file_path for file_path in file_paths if file_path.suffix == '.csv']

    assert len(manifests) == 3, 'Incorrect number of manifest files'

    with open(Path('acceptance_test_batch.csv')) as batch_config:
        config_file = list(csv.DictReader(batch_config))

    for index, print_file in enumerate(print_files):
        with open(print_file) as print_file_handler:
            print_file_reader = csv.DictReader(print_file_handler, delimiter='|', fieldnames=PRINT_FILE_TEMPLATE)

            row_counter = 0
            for row in print_file_reader:
                row_counter += 1
                assert len(row['UAC']) == 16, 'Incorrect UAC length'
                assert row['PRODUCTPACK_CODE'] == config_file[index]['Pack code'], \
                    'PRODUCTPACK_CODE does not match config'
                assert row['QUESTIONNAIRE_ID'][:2] == config_file[index]['Questionnaire type'], \
                    'QUESTIONNAIRE_ID does not match config'
            assert row_counter == int(config_file[index]['Quantity']), 'Print file row count does not match config'


def test_valid_print_files_are_produced_for_a_qid_batch():
    # Given
    batch_id = uuid.uuid4()
    with rabbit_connection_and_channel() as (connection, channel):
        generate_test_qid_batch(batch_id)
        wait_for_uacs_to_be_created(connection, channel)

    # When
    file_paths = generate_print_files_from_config_file_path(Path('acceptance_test_batch.csv'), Path('.'),
                                                            batch_id)

    # Then
    validate_print_file_data(file_paths)


if __name__ == '__main__':
    test_valid_print_files_are_produced_for_a_qid_batch()
