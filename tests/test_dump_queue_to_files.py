import json
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from dump_queue_to_files import _rabbit_message_received_callback, dump_messages


def test_rabbit_message_consume(cleanup_test_files: Path):
    output_file_path = cleanup_test_files.joinpath(f'{str(uuid.uuid4())}.dump')

    for i in range(5):  # simulate publishing 5 messages
        message = f'{{"{i}_entry":"{i}_value"}}'.encode('utf-8')
        _rabbit_message_received_callback(Mock(), Mock(), None, message, output_file_path)

    for file_count, file_path in enumerate(cleanup_test_files.rglob('*.dump'), start=1):
        with file_path.open() as message_file:
            for index, message_line in enumerate(message_file):
                assert json.loads(message_line)[f'{index}_entry'] == f'{index}_value'

    assert file_count == 1, f"should only be a single *.dump file (not {file_count} files)"


def test_directory_path_name(cleanup_test_files: Path):
    test_datetime = datetime(2019, 8, 30, 17, 00, 00, 0)
    with patch('dump_queue_to_files.datetime') as patched_dt:
        patched_dt.utcnow.return_value = test_datetime
        with patch('dump_queue_to_files.RabbitContext'):
            directory_path = dump_messages('test-queue', cleanup_test_files)

    assert 'test-queue_2019-08-30T17-00-00' in str(directory_path)
