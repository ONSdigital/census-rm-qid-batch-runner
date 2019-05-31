import json
import uuid
from pathlib import Path
from unittest.mock import patch

from generate_qid_batch import generate_messages_from_config_file_path


def test_generate_messages_from_config_file_path_publishes_correct_quantities():
    # Given
    batch_id = uuid.uuid4()

    # When
    publish_message_call_list = generate_messages_with_mocked_rabbit('test_batch.csv', batch_id)

    # Then
    assert json.loads(publish_message_call_list[0][0][0])['questionnaireType'] == '01'
    assert json.loads(publish_message_call_list[1][0][0])['questionnaireType'] == '01'
    assert json.loads(publish_message_call_list[2][0][0])['questionnaireType'] == '02'
    assert len(publish_message_call_list) == 3


def test_generate_messages_from_config_file_path_sets_batch_id():
    # Given
    batch_id = uuid.uuid4()

    # When
    publish_message_call_list = generate_messages_with_mocked_rabbit('test_batch.csv', batch_id)

    # Then
    assert all(json.loads(message[0][0])['batchId'] == str(batch_id) for message in publish_message_call_list)


def generate_messages_with_mocked_rabbit(config_file_name, batch_id):
    config_file_path = Path(__file__).parent.resolve().joinpath('resources').joinpath(config_file_name)
    with patch('generate_qid_batch.RabbitContext') as patch_rabbit:
        generate_messages_from_config_file_path(config_file_path, batch_id)
    return patch_rabbit.return_value.__enter__.return_value.publish_message.call_args_list
