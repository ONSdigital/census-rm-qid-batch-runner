from unittest.mock import Mock

from dump_queue_to_files import _rabbit_message_received_callback


def test_rabbit_message_consume(cleanup_test_files):
    file_paths = []
    _rabbit_message_received_callback(Mock(), Mock(), None, b'{"key":"value"}', 1, cleanup_test_files, file_paths)

    index = 0

    for index, file_path in enumerate(cleanup_test_files.rglob('*.json')):
        with open(file_path) as message_file:
            assert '{"key":"value"}' == message_file.read()

    assert index + 1 == 1
