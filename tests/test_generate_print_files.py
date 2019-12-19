import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, Mock, call

import paramiko
import pgpy
import pytest

from exceptions import QidQuantityMismatchException
from generate_print_files import generate_print_files_from_config_file_path, copy_files_to_gcs, copy_files_to_sftp


def test_generate_print_files_from_config_file_path_generates_correct_print_file_contents(cleanup_test_files,
                                                                                          mock_db_engine,
                                                                                          setup_environment):
    # Given
    resource_file_path = setup_environment
    config_file_path = resource_file_path.joinpath('test_batch.csv')
    batch_id = uuid.uuid4()
    mock_test_batch_results(mock_db_engine, batch_id)

    # When
    generate_print_files_from_config_file_path(config_file_path, cleanup_test_files, batch_id)

    # Then
    our_key, _ = pgpy.PGPKey.from_file(Path(__file__).parents[1].joinpath('dummy_keys', 'our_dummy_private.asc'))

    encrypted_message_1 = pgpy.PGPMessage.from_file(next(cleanup_test_files.glob('D_FD_H1*.csv')))
    encrypted_message_2 = pgpy.PGPMessage.from_file(next(cleanup_test_files.glob('D_FD_H2*.csv')))
    with our_key.unlock(passphrase='test'):
        message_1 = our_key.decrypt(encrypted_message_1).message
        message_2 = our_key.decrypt(encrypted_message_2).message
    assert message_1 == ('test_uac_1|test_qid_1||||||||||||D_FD_H1\r\n'
                         'test_uac_2|test_qid_2||||||||||||D_FD_H1\r\n')
    assert message_2 == 'test_uac_3|test_qid_3||||||||||||D_FD_H2\r\n'


def test_unaddressed_ccs_print_files_leaves_out_UAC(cleanup_test_files,
                                                    mock_db_engine,
                                                    setup_environment):
    # Given
    resource_file_path = setup_environment
    config_file_path = resource_file_path.joinpath('ccs_test_batch.csv')
    batch_id = uuid.uuid4()
    mock_ccs_test_batch_results(mock_db_engine, batch_id)

    # When
    generate_print_files_from_config_file_path(config_file_path, cleanup_test_files, batch_id)

    # Then
    our_key, _ = pgpy.PGPKey.from_file(Path(__file__).parents[1].joinpath('dummy_keys', 'our_dummy_private.asc'))

    encrypted_message = pgpy.PGPMessage.from_file(next(cleanup_test_files.glob('D_CCS_CHP2W*.csv')))
    with our_key.unlock(passphrase='test'):
        message = our_key.decrypt(encrypted_message).message
    assert message == '|test_qid_1||||||||||||D_CCS_CHP2W\r\n'


def test_generate_print_files_from_config_file_path_generates_correct_print_file_names(cleanup_test_files,
                                                                                       mock_db_engine,
                                                                                       setup_environment):
    # Given
    resource_file_path = setup_environment
    config_file_path = resource_file_path.joinpath('test_batch.csv')
    batch_id = uuid.uuid4()
    mock_test_batch_results(mock_db_engine, batch_id)

    # When
    with patch('generate_print_files.datetime') as patched_datetime:
        # Patch the datetime to return a fixed time we can test against
        patched_datetime.utcnow.return_value = datetime(2013, 9, 30, 7, 6, 5)
        generate_print_files_from_config_file_path(config_file_path, cleanup_test_files, batch_id)

    # Then
    assert cleanup_test_files.joinpath('D_FD_H1_2013-09-30T07-06-05.csv').exists()
    assert cleanup_test_files.joinpath('D_FD_H2_2013-09-30T07-06-05.csv').exists()


def test_generate_print_files_from_config_file_path_errors_on_qid_quantity_mismatch(cleanup_test_files,
                                                                                    mock_db_engine,
                                                                                    setup_environment):
    # Given
    resource_file_path = setup_environment
    batch_id = uuid.uuid4()
    mock_test_batch_results(mock_db_engine, batch_id)

    # When
    config_file_path = resource_file_path.joinpath('test_batch_quantity_mismatch.csv')

    # Then
    with pytest.raises(QidQuantityMismatchException, match='expected = 10, found = 2, questionnaire type = 01'):
        generate_print_files_from_config_file_path(config_file_path, cleanup_test_files, batch_id)


def test_generate_print_files_from_config_file_path_generates_correct_manifests(cleanup_test_files,
                                                                                mock_db_engine,
                                                                                setup_environment):
    # Given
    resource_file_path = setup_environment
    config_file_path = resource_file_path.joinpath('test_batch.csv')
    batch_id = uuid.uuid4()
    mock_test_batch_results(mock_db_engine, batch_id)

    # When
    generate_print_files_from_config_file_path(config_file_path, cleanup_test_files, batch_id)

    # Then
    manifest_file_1 = next(cleanup_test_files.glob('D_FD_H1*.manifest'))
    manifest_1 = json.loads(manifest_file_1.read_text())
    assert manifest_1['description'] == 'Household Questionnaire pack for England'
    assert manifest_1['files'][0]['sizeBytes'] == '1634'
    assert manifest_1['files'][0]['name'] == f'{manifest_file_1.stem}.csv'
    assert manifest_1['files'][0]['relativePath'].startswith('./')
    assert manifest_1['sourceName'] == 'ONS_RM'

    manifest_file_2 = next(cleanup_test_files.glob('D_FD_H2*.manifest'))
    manifest_2 = json.loads(manifest_file_2.read_text())
    assert manifest_2['description'] == 'Household Questionnaire pack for Wales (English)'
    assert manifest_2['files'][0]['sizeBytes'] == '1626'
    assert manifest_2['files'][0]['name'] == f'{manifest_file_2.stem}.csv'
    assert manifest_2['files'][0]['relativePath'].startswith('./')
    assert manifest_2['sourceName'] == 'ONS_RM'


def test_copy_files_to_gcs():
    # Given
    test_files = [Path('test1'), Path('test2'), Path('test3')]
    mock_storage_client = Mock()

    # When
    with patch('generate_print_files.storage') as patched_storage:
        patched_storage.Client.return_value = mock_storage_client
        copy_files_to_gcs(test_files)

    mock_upload_from_filename = mock_storage_client.get_bucket.return_value.blob.return_value.upload_from_filename

    # Then
    mock_upload_from_filename.assert_has_calls([call(filename=str(file_path)) for file_path in test_files])


def test_copy_files_to_sftp():
    # Given
    test_files = [Path('test1'), Path('test2'), Path('test3')]
    os.environ['SFTP_DIRECTORY'] = 'test_path'
    mock_storage_client = Mock()

    # When
    with patch('generate_print_files.sftp.paramiko.SSHClient') as client:
        client.return_value.open_sftp.return_value = mock_storage_client  # mock the sftp client connection
        mock_storage_client.stat.return_value.st_mode = paramiko.sftp_client.stat.S_IFDIR  # mock directory exists
        copy_files_to_sftp(test_files)

    mock_put_file = mock_storage_client.put

    # Then
    mock_put_file.assert_has_calls(
        [call(str(file_path), file_path.name) for file_path in test_files])


def mock_test_batch_results(mock_engine, batch_id: uuid.UUID):
    mock_engine.execute.side_effect = (
        ({'qid': 'test_qid_1', 'uac': 'test_uac_1', 'batch_id': str(batch_id)},
         {'qid': 'test_qid_2', 'uac': 'test_uac_2', 'batch_id': str(batch_id)}),
        ({'qid': 'test_qid_3', 'uac': 'test_uac_3', 'batch_id': str(batch_id)},)
    )


def mock_ccs_test_batch_results(mock_engine, batch_id: uuid.UUID):
    mock_engine.execute.side_effect = (({'qid': 'test_qid_1', 'uac': 'test_uac_1', 'batch_id': str(batch_id)},),)


@pytest.fixture
def setup_environment():
    resource_file_path = Path(__file__).parent.resolve().joinpath('resources')
    required_env_vars = ('DB_PORT', 'DB_HOST', 'DB_NAME', 'DB_USERNAME', 'DB_PASSWORD')
    for env_var in required_env_vars:
        os.environ[env_var] = 'test_value'
    os.environ['OTHER_PUBLIC_KEY_PATH'] = str(
        Path(__file__).parents[1].joinpath('dummy_keys', 'supplier_dummy_public.asc'))
    os.environ['OUR_PUBLIC_KEY_PATH'] = str(Path(__file__).parents[1].joinpath('dummy_keys', 'our_dummy_public.asc'))
    return resource_file_path


@pytest.fixture
def mock_db_engine():
    mock_engine = Mock()
    with patch('generate_print_files.create_engine') as patched_create_engine:
        patched_create_engine.return_value = mock_engine
        yield mock_engine
