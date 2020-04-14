import argparse
import csv
import hashlib
import io
import json
import os
import urllib
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Collection

from google.cloud import storage
from sqlalchemy import create_engine
from sqlalchemy.sql import text

import sftp
from encryption import pgp_encrypt_message
from exceptions import QidQuantityMismatchException
from mappings import SUPPLIER_TO_SFTP_DIRECTORY, PRODUCTPACK_CODE_TO_DESCRIPTION, SUPPLIER_TO_PRINT_TEMPLATE, \
    PRODUCTPACK_CODE_TO_DATASET


def _get_uac_qid_links(engine, questionnaire_type, batch_id: uuid.UUID):
    uac_qid_links_query = text("SELECT * FROM casev2.uac_qid_link WHERE SUBSTRING(qid FROM 1 FOR 2)"
                               " = :questionnaire_type AND caze_case_id IS NULL AND batch_id = :batch_id")

    return engine.execute(uac_qid_links_query, questionnaire_type=questionnaire_type, batch_id=str(batch_id))


def create_db_engine():
    db_port = os.getenv('DB_PORT', '6432')
    db_name = os.getenv('DB_NAME', 'postgres')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_username = os.getenv('DB_USERNAME', 'postgres')
    db_password = urllib.parse.quote_plus(os.getenv('DB_PASSWORD', 'postgres'))
    db_uri = f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'
    return create_engine(db_uri)


def generate_print_files_from_config_file_path(config_file_path: Path,
                                               output_file_path: Path,
                                               batch_id: uuid.UUID, supplier) -> List[Path]:
    with open(config_file_path) as config_file:
        return generate_print_files_from_config_file(config_file, output_file_path, batch_id, supplier)


def generate_print_files_from_config_file(config_file, output_file_path: Path, batch_id: uuid.UUID, supplier) \
        -> List[Path]:
    config_file_reader = csv.DictReader(config_file)
    db_engine = create_db_engine()
    file_paths = []
    for config_row in config_file_reader:
        uac_qid_links = _get_uac_qid_links(db_engine, config_row['Questionnaire type'], batch_id)
        filename = f'{config_row["Pack code"]}_{datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")}'
        print_file_path = output_file_path.joinpath(f'{filename}.csv.gpg')
        generate_print_file(print_file_path, uac_qid_links, config_row, supplier)
        file_paths.append(print_file_path)
        manifest_file_path = output_file_path.joinpath(f'{filename}.manifest')
        generate_manifest_file(manifest_file_path, print_file_path, config_row['Pack code'])
        file_paths.append(manifest_file_path)
    print(f'Successfully generated {len(file_paths)} files in {output_file_path}')
    return file_paths


def generate_print_file(print_file_path: Path, uac_qid_links, config, supplier):
    with io.StringIO() as print_file_stream:
        csv_writer = csv.DictWriter(print_file_stream, fieldnames=SUPPLIER_TO_PRINT_TEMPLATE[supplier], delimiter='|')

        row_builder = build_ccs_print_row if is_ccs_pack_code(config['Pack code']) else build_print_row

        row_count = 0

        for row_count, result_row in enumerate(uac_qid_links, start=1):
            print_row = row_builder(result_row, config)
            csv_writer.writerow(print_row)
        if row_count != int(config["Quantity"]):
            raise QidQuantityMismatchException(f'expected = {config["Quantity"]}, found = {row_count}, '
                                               f'questionnaire type = {config["Questionnaire type"]}')
        unencrypted_csv_contents = print_file_stream.getvalue()

    encrypted_csv_message = pgp_encrypt_message(unencrypted_csv_contents, supplier)

    with open(print_file_path, 'w') as print_file:
        print_file.write(encrypted_csv_message)


def is_ccs_pack_code(pack_code):
    return pack_code.startswith('D_CCS')


def build_print_row(result_row, config):
    return {'UAC': result_row['uac'], 'QUESTIONNAIRE_ID': result_row['qid'], 'PRODUCTPACK_CODE': config["Pack code"]}


def build_ccs_print_row(result_row, config):
    return {'QUESTIONNAIRE_ID': result_row['qid'], 'PRODUCTPACK_CODE': config["Pack code"]}


def generate_manifest_file(manifest_file_path: Path, print_file_path: Path, productpack_code: str):
    manifest = create_manifest(print_file_path, productpack_code)
    manifest_file_path.write_text(json.dumps(manifest))


def create_manifest(print_file_path: Path, productpack_code: str) -> dict:
    return {
        'schemaVersion': '1',
        'description': PRODUCTPACK_CODE_TO_DESCRIPTION[productpack_code],
        'dataset': PRODUCTPACK_CODE_TO_DATASET[productpack_code].value,
        'version': '1',
        'manifestCreated': datetime.utcnow().isoformat(timespec='milliseconds') + 'Z',
        'sourceName': 'ONS_RM',
        'files': [
            {
                'name': print_file_path.name,
                'relativePath': './',
                'sizeBytes': str(print_file_path.stat().st_size),
                'md5sum': hashlib.md5(print_file_path.read_text().encode()).hexdigest()
            }
        ]
    }


def copy_files_to_gcs(file_paths: Collection[Path]):
    client = storage.Client()
    bucket = client.get_bucket(f'{client.project}-print-files')
    print(f'Copying files to GCS bucket {bucket.name}')
    for file_path in file_paths:
        bucket.blob(file_path.name).upload_from_filename(filename=str(file_path))
    print(f'All {len(file_paths)} files successfully written to {bucket.name}')


def copy_files_to_sftp(file_paths: Collection[Path], supplier):
    sftp_directory = SUPPLIER_TO_SFTP_DIRECTORY[supplier]
    with sftp.SftpUtility(sftp_directory) as sftp_client:
        print(f'Copying files to SFTP remote {sftp_client.sftp_directory}')
        for file_path in file_paths:
            sftp_client.put_file(local_path=str(file_path), filename=file_path.name)
        print(f'All {len(file_paths)} files successfully written to {sftp_client.sftp_directory}')


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Generate a print file from a CSV config file specifying questionnaire types and respective '
                    'QID/UAC counts')
    parser.add_argument('config_file_path', help='Path to the CSV config file', type=Path)
    parser.add_argument('output_file_path', help='Directory to write output files', type=Path)
    parser.add_argument('supplier', help="The supplier the files are going to", type=str)
    parser.add_argument('batch_id', help='UUID for this qid/uac pair batch, defaults to randomly generated',
                        type=uuid.UUID)
    parser.add_argument('--no-gcs', help="Don't copy the files to a GCS bucket", required=False, action='store_true')
    parser.add_argument('--no-sftp', help="Don't copy the files over SFTP", required=False, action='store_true')
    return parser.parse_args()


def main():
    args = parse_arguments()
    print(args.config_file_path)
    file_paths = generate_print_files_from_config_file_path(args.config_file_path, args.output_file_path, args.batch_id,
                                                            args.supplier)
    if not args.no_gcs:
        copy_files_to_gcs(file_paths)
    if not args.no_sftp:
        copy_files_to_sftp(file_paths, args.supplier)


if __name__ == '__main__':
    main()
