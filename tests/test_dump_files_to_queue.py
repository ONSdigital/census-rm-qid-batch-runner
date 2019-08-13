import json
from pathlib import Path
from unittest.mock import patch

from dump_files_to_queue import publish_messages_from_dump_files


def test_publish_messages_from_config_file_path(cleanup_test_files):
    resource_file_path = Path(__file__).parent.resolve().joinpath('resources')
    test_message_path = resource_file_path.joinpath('test_message.dump')
    test_text = ('{"first_item":"1"}\n', '{"second_item":"2"}\n')
    with test_message_path.open('w') as fh:
        fh.writelines(test_text)

    with patch('dump_files_to_queue.RabbitContext') as patch_rabbit:
        publish_messages_from_dump_files("dummy", resource_file_path, cleanup_test_files)

    for file_count, file_path in enumerate(cleanup_test_files.rglob('*.dump'), 1):
        with file_path.open() as message_file:
            for file_line, test_line in zip(list(message_file), test_text):
                assert file_line == test_line

    assert file_count == 1, "should be a single *.dump file"

    call_list = patch_rabbit.return_value.__enter__.return_value.publish_message.call_args_list
    assert len(call_list) == 2
    assert json.loads(call_list[0][0][0])['first_item'] == '1'
    assert json.loads(call_list[1][0][0])['second_item'] == '2'
