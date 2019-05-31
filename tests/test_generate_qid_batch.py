import json
import uuid
from pathlib import Path
from unittest.mock import patch

from generate_qid_batch import generate_messages_from_config_file_path


def test_generate_messages_from_config_file_path():
    # Given
    config_file_path = Path(__file__).parent.resolve().joinpath('resources').joinpath('test_batch.csv')

    # When
    with patch('generate_qid_batch.RabbitContext') as patch_rabbit:
        generate_messages_from_config_file_path(config_file_path, uuid.uuid4())

    # Then
    patch_rabbit_context = patch_rabbit.return_value.__enter__.return_value
    publish_message_call_list = patch_rabbit_context.publish_message.call_args_list

    assert json.loads(publish_message_call_list[0][0][0])['questionnaireType'] == '01'
    assert json.loads(publish_message_call_list[1][0][0])['questionnaireType'] == '01'
    assert json.loads(publish_message_call_list[2][0][0])['questionnaireType'] == '02'
