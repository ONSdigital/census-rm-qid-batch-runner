import json
import os
import shutil
from pathlib import Path
from unittest.mock import patch, Mock, call

import pytest

from generate_print_files import generate_print_files_from_config_file_path, copy_files_to_gcs


def test_generate_print_files_from_config_file_path_generates_correct_print_files(cleanup_test_files,
                                                                                  mock_db_engine,
                                                                                  setup_environment):
    # Given
    config_file_path, output_file_path = setup_environment

    # When
    generate_print_files_from_config_file_path(config_file_path, output_file_path)

    # Then
    assert next(output_file_path.glob('D_FD_H1*.csv')).read_text() == ('test_uac_1|test_qid_1|||||||||||D_FD_H1\n'
                                                                       'test_uac_2|test_qid_2|||||||||||D_FD_H1\n')
    assert next(output_file_path.glob('D_FD_H2*.csv')).read_text() == 'test_uac_3|test_qid_3|||||||||||D_FD_H2\n'


def test_generate_print_files_from_config_file_path_generates_correct_manifests(cleanup_test_files,
                                                                                mock_db_engine,
                                                                                setup_environment):
    # Given
    config_file_path, output_file_path = setup_environment

    # When
    generate_print_files_from_config_file_path(config_file_path, output_file_path)

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


@pytest.fixture
def setup_environment():
    config_file_path = Path(__file__).parent.resolve().joinpath('resources').joinpath('test_batch.csv')
    output_file_path = Path(__file__).parent.resolve().joinpath('tmp_test_files')

    required_env_vars = ('DB_PORT', 'DB_HOST', 'DB_NAME', 'DB_USERNAME', 'DB_PASSWORD')
    for env_var in required_env_vars:
        os.environ[env_var] = 'test_value'
    return config_file_path, output_file_path


@pytest.fixture
def mock_db_engine():
    mock_engine = Mock()
    mock_engine.execute.side_effect = (
        ({'qid': 'test_qid_1', 'uac': 'test_uac_1'},
         {'qid': 'test_qid_2', 'uac': 'test_uac_2'}),
        ({'qid': 'test_qid_3', 'uac': 'test_uac_3'},)
    )
    with patch('generate_print_files.create_engine') as patched_create_engine:
        patched_create_engine.return_value = mock_engine
        yield


@pytest.fixture
def cleanup_test_files():
    test_file_path = Path(__file__).parent.resolve().joinpath('tmp_test_files')
    if test_file_path.exists():
        shutil.rmtree(test_file_path)
    test_file_path.mkdir()
    yield
    shutil.rmtree(test_file_path)