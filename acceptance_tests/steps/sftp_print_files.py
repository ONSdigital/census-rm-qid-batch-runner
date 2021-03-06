import os
from pathlib import Path

from behave import given, when, then, step

from mappings import SUPPLIER_TO_SFTP_DIRECTORY
from sftp import SftpUtility
from generate_print_files import copy_files_to_sftp


@given('the print files have been previously generated from the "{sample_file}"')
def print_files_exist(context, sample_file):
    context.file_paths = list(Path(__file__).parents[1].resolve().joinpath('resources').glob(f'{sample_file}.*'))
    for fp in context.file_paths:
        assert fp.is_file()


@step('the correct SFTP config has been provided')
def sftp_config_exists(context):
    required_env_vars = (
        'SFTP_QM_DIRECTORY', 'SFTP_PPO_DIRECTORY', 'SFTP_HOST', 'SFTP_USERNAME', 'SFTP_KEY_FILENAME', 'SFTP_PASSPHRASE')
    for env_var in required_env_vars:
        assert os.environ[env_var] is not None


@when('the SFTP utility is used to copy the print files to the "{directory}" directory')
def upload_print_files_to_sftp(context, directory):
    copy_files_to_sftp(context.file_paths, directory)


@then('the print files are present on the remote "{supplier}" SFTP')
def check_print_files_are_in_sftp(context, supplier):
    with SftpUtility(SUPPLIER_TO_SFTP_DIRECTORY[supplier]) as sftp_client:
        sftp_contents = sftp_client._sftp_client.listdir('.')
        assert all(fp.name in sftp_contents for fp in context.file_paths)
        for fp in context.file_paths:
            sftp_client._sftp_client.remove(fp.name)
