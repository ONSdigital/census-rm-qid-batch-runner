import json
import shutil
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from generate_print_files import generate_print_files_from_config_file_path


def test_generate_print_files_from_config_file_path_generates_correct_print_files(cleanup_test_files):
    # Given
    config_file_path, mock_engine, output_file_path = setup_files_and_mocks()

    # When
    generate_print_files_with_mock_engine(config_file_path, mock_engine, output_file_path)

    # Then
    assert next(output_file_path.glob('D_FD_H1*.csv')).read_text() == ('test_uac_1|test_qid_1||||||||D_FD_H1\n'
                                                                       'test_uac_2|test_qid_2||||||||D_FD_H1\n')
    assert next(output_file_path.glob('D_FD_H2*.csv')).read_text() == 'test_uac_3|test_qid_3||||||||D_FD_H2\n'


def test_generate_print_files_from_config_file_path_generates_correct_manifests(cleanup_test_files):
    # Given
    config_file_path, mock_engine, output_file_path = setup_files_and_mocks()

    # When
    generate_print_files_with_mock_engine(config_file_path, mock_engine, output_file_path)

    # Then
    manifest_file_1 = next(output_file_path.glob('D_FD_H1*.manifest'))
    manifest_1 = json.loads(manifest_file_1.read_text())
    assert manifest_1['description'] == 'Household Questionnaire pack for England'
    assert manifest_1['files'][0]['sizeBytes'] == '76'
    assert manifest_1['files'][0]['md5Sum'] == '9497defb064132b990c70ceefe99a3b9'
    assert manifest_1['files'][0]['name'] == f'{manifest_file_1.stem}.csv'

    manifest_file_2 = next(output_file_path.glob('D_FD_H2*.manifest'))
    manifest_2 = json.loads(manifest_file_2.read_text())
    assert manifest_2['description'] == 'Household Questionnaire pack for Wales (English)'
    assert manifest_2['files'][0]['sizeBytes'] == '38'
    assert manifest_2['files'][0]['md5Sum'] == '85286b8006f6da1706d937cfed9b8e31'
    assert manifest_2['files'][0]['name'] == f'{manifest_file_2.stem}.csv'


def generate_print_files_with_mock_engine(config_file_path, mock_engine, output_file_path):
    with patch('generate_print_files.create_db_engine') as patched_created_db_engine:
        patched_created_db_engine.return_value = mock_engine
        generate_print_files_from_config_file_path(config_file_path, output_file_path)


def setup_files_and_mocks():
    config_file_path = Path(__file__).parent.resolve().joinpath('resources').joinpath('test_batch.csv')
    output_file_path = Path(__file__).parent.resolve().joinpath('tmp_test_files')
    mock_engine = Mock()
    mock_engine.execute.side_effect = (
        ({'qid': 'test_qid_1', 'uac': 'test_uac_1'},
         {'qid': 'test_qid_2', 'uac': 'test_uac_2'}),
        ({'qid': 'test_qid_3', 'uac': 'test_uac_3'},)
    )
    return config_file_path, mock_engine, output_file_path


@pytest.fixture
def cleanup_test_files():
    test_file_path = Path(__file__).parent.resolve().joinpath('tmp_test_files')
    if test_file_path.exists():
        shutil.rmtree(test_file_path)
    test_file_path.mkdir()
    yield
    shutil.rmtree(test_file_path)
