import json
import os
import shutil
import uuid
from pathlib import Path
from unittest.mock import patch, Mock, call

import pytest

from exceptions import QidQuantityMismatchException
from generate_print_files import generate_print_files_from_config_file_path, copy_files_to_gcs, copy_files_to_sftp


def test_generate_print_files_from_config_file_path_generates_correct_print_files(cleanup_test_files,
                                                                                  mock_db_engine,
                                                                                  setup_environment):
    # Given
    resource_file_path, output_file_path = setup_environment
    config_file_path = resource_file_path.joinpath('test_batch.csv')
    batch_id = uuid.uuid4()
    mock_test_batch_results(mock_db_engine, batch_id)

    # When
    generate_print_files_from_config_file_path(config_file_path, output_file_path, batch_id)

    # Then
    assert next(output_file_path.glob('D_FD_H1*.csv')).read_text() == ('test_uac_1|test_qid_1|||||||||||D_FD_H1\n'
                                                                       'test_uac_2|test_qid_2|||||||||||D_FD_H1\n')
    assert next(output_file_path.glob('D_FD_H2*.csv')).read_text() == 'test_uac_3|test_qid_3|||||||||||D_FD_H2\n'


def test_generate_print_files_from_config_file_path_errors_on_qid_quantity_mismatch(cleanup_test_files,
                                                                                    mock_db_engine,
                                                                                    setup_environment):
    # Given
    resource_file_path, output_file_path = setup_environment
    batch_id = uuid.uuid4()
    mock_test_batch_results(mock_db_engine, batch_id)

    # When
    config_file_path = resource_file_path.joinpath('test_batch_quantity_mismatch.csv')

    # Then
    with pytest.raises(QidQuantityMismatchException, match='expected = 10, found = 2, questionnaire type = 01'):
        generate_print_files_from_config_file_path(config_file_path, output_file_path, batch_id)


def test_generate_print_files_from_config_file_path_generates_correct_manifests(cleanup_test_files,
                                                                                mock_db_engine,
                                                                                setup_environment):
    # Given
    resource_file_path, output_file_path = setup_environment
    config_file_path = resource_file_path.joinpath('test_batch.csv')
    batch_id = uuid.uuid4()
    mock_test_batch_results(mock_db_engine, batch_id)

    # When
    generate_print_files_from_config_file_path(config_file_path, output_file_path, batch_id)

    # Then
    manifest_file_1 = next(output_file_path.glob('D_FD_H1*.manifest'))
    manifest_1 = json.loads(manifest_file_1.read_text())
    assert manifest_1['description'] == 'Household Questionnaire pack for England'
    assert manifest_1['files'][0]['sizeBytes'] == '82'
    assert manifest_1['files'][0]['md5Sum'] == 'ba54b332897525b3318a45509f53a12c'
    assert manifest_1['files'][0]['name'] == f'{manifest_file_1.stem}.csv'

    manifest_file_2 = next(output_file_path.glob('D_FD_H2*.manifest'))
    manifest_2 = json.loads(manifest_file_2.read_text())
    assert manifest_2['description'] == 'Household Questionnaire pack for Wales (English)'
    assert manifest_2['files'][0]['sizeBytes'] == '41'
    assert manifest_2['files'][0]['md5Sum'] == 'c346a4404612e58408fad219725b1720'
    assert manifest_2['files'][0]['name'] == f'{manifest_file_2.stem}.csv'


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
        client.return_value.open_sftp.return_value = mock_storage_client
        copy_files_to_sftp(test_files)

    mock_put_file = mock_storage_client.put

    # Then
    mock_put_file.assert_has_calls(
        [call(str(file_path), f'test_path/{file_path.name}') for file_path in test_files])


def mock_test_batch_results(mock_engine, batch_id: uuid.UUID):
    mock_engine.execute.side_effect = (
        ({'qid': 'test_qid_1', 'uac': 'test_uac_1', 'batch_id': str(batch_id)},
         {'qid': 'test_qid_2', 'uac': 'test_uac_2', 'batch_id': str(batch_id)}),
        ({'qid': 'test_qid_3', 'uac': 'test_uac_3', 'batch_id': str(batch_id)},)
    )


@pytest.fixture
def setup_environment():
    resource_file_path = Path(__file__).parent.resolve().joinpath('resources')
    output_file_path = Path(__file__).parent.resolve().joinpath('tmp_test_files')

    required_env_vars = ('DB_PORT', 'DB_HOST', 'DB_NAME', 'DB_USERNAME', 'DB_PASSWORD')
    for env_var in required_env_vars:
        os.environ[env_var] = 'test_value'
    return resource_file_path, output_file_path


@pytest.fixture
def mock_db_engine():
    mock_engine = Mock()
    with patch('generate_print_files.create_engine') as patched_create_engine:
        patched_create_engine.return_value = mock_engine
        yield mock_engine


@pytest.fixture
def cleanup_test_files():
    test_file_path = Path(__file__).parent.resolve().joinpath('tmp_test_files')
    if test_file_path.exists():
        shutil.rmtree(test_file_path)
    test_file_path.mkdir()
    yield
    shutil.rmtree(test_file_path)
