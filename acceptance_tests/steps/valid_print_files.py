import csv
import io
import os
import uuid
from contextlib import contextmanager
from pathlib import Path

import pgpy
import pika
from behave import given, when, then

from generate_print_files import PRINT_FILE_TEMPLATE, generate_print_files_from_config_file_path
from generate_qid_batch import generate_messages_from_config_file_path


@given('a QID batch has been generated')
def generate_test_qid_batch(context):
    context.batch_config_path = Path(__file__).parents[1].resolve().joinpath('resources', 'acceptance_test_batch.csv')
    context.batch_id = uuid.uuid4()
    with rabbit_connection_and_channel() as (connection, channel):
        request_test_qid_batch(context.batch_id)
        wait_for_uacs_to_be_created(connection, channel)


def request_test_qid_batch(batch_id):
    generate_messages_from_config_file_path(
        Path(__file__).parents[1].resolve().joinpath('resources', 'acceptance_test_batch.csv'),
        batch_id)


def wait_for_uacs_to_be_created(connection, channel, timeout=30, expected_quantity=30):
    def message_callback(channel, method, *_):
        nonlocal uac_message_count
        uac_message_count += 1
        channel.basic_ack(delivery_tag=method.delivery_tag)
        if uac_message_count >= expected_quantity:
            channel.stop_consuming()

    def timeout_callback():
        assert False, 'Timed out waiting for messages'

    uac_message_count = 0
    connection.call_later(timeout, timeout_callback)
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


@when('the print files are generated')
def generate_print_files(context):
    context.print_file_paths = generate_print_files_from_config_file_path(
        context.batch_config_path, Path('.'), context.batch_id)


@then('the contents of the print files are valid')
def validate_print_file_data(context):
    manifests = [file_path for file_path in context.print_file_paths if file_path.suffix == '.manifest']
    print_files = [file_path for file_path in context.print_file_paths if file_path.suffix == '.csv']

    assert len(manifests) == 4, 'Incorrect number of manifest files'

    with open(context.batch_config_path) as batch_config:
        config_file = list(csv.DictReader(batch_config))

    our_key, _ = pgpy.PGPKey.from_file('dummy_keys/our_dummy_private.asc')
    supplier_key, _ = pgpy.PGPKey.from_file('dummy_keys/supplier_dummy_private.asc')

    check_encrypted_files(print_files, config_file, our_key, passphrase='test')
    check_encrypted_files(print_files, config_file, supplier_key, passphrase='supplier')


def check_encrypted_files(print_files, config_file, key, passphrase):
    for index, print_file in enumerate(print_files):

        encrypted_print_file_csv = pgpy.PGPMessage.from_file(print_file)

        with key.unlock(passphrase=passphrase):
            print_file_csv = key.decrypt(encrypted_print_file_csv).message

        print_file_reader = csv.DictReader(io.StringIO(print_file_csv),  # NB: requires a file-like object not string
                                           delimiter='|',
                                           lineterminator='\r\n',
                                           fieldnames=PRINT_FILE_TEMPLATE)

        if print_file.name.startswith('D_CCS'):
            for row_count, row in enumerate(print_file_reader, start=1):
                assert not row['UAC'], ('UAC should not exist on CCS unaddressed print file', row['UAC'])
                assert row['PRODUCTPACK_CODE'] == config_file[index]['Pack code'], \
                    ('PRODUCTPACK_CODE does not match config', row['PRODUCTPACK_CODE'])
                assert row['QUESTIONNAIRE_ID'][:2] == config_file[index]['Questionnaire type'], \
                    'QUESTIONNAIRE_ID does not match config'

        else:
            for row_count, row in enumerate(print_file_reader, start=1):
                assert len(row['UAC']) == 16, ('Incorrect UAC length', row['UAC'])
                assert row['PRODUCTPACK_CODE'] == config_file[index]['Pack code'], \
                    ('PRODUCTPACK_CODE does not match config', row['PRODUCTPACK_CODE'])
                assert row['QUESTIONNAIRE_ID'][:2] == config_file[index]['Questionnaire type'], \
                    'QUESTIONNAIRE_ID does not match config'

        assert row_count == int(
            config_file[index]['Quantity']), ('Print file row count does not match config', row_count)
