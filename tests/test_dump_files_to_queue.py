import json
from pathlib import Path
from unittest.mock import patch

from dump_files_to_queue import publish_messages_from_config_file_path


def test_publish_messages_from_config_file_path(cleanup_test_files):
    resource_file_path = Path(__file__).parent.resolve().joinpath('resources')
    test_message_path = resource_file_path.joinpath('test_message.json')
    test_message_path.write_text('{"foo":"bar"}')

    with patch('dump_files_to_queue.RabbitContext') as patch_rabbit:
        publish_messages_from_config_file_path("dummy", resource_file_path, cleanup_test_files)

    index = 0

    for index, file_path in enumerate(cleanup_test_files.rglob('*.json')):
        with open(file_path) as message_file:
            assert '{"foo":"bar"}' == message_file.read()

    assert index + 1 == 1

    call_list = patch_rabbit.return_value.__enter__.return_value.publish_message.call_args_list
    assert len(call_list) == 1
    assert json.loads(call_list[0][0][0])['foo'] == 'bar'
