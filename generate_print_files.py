import argparse
import csv
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Collection

from google.cloud import storage
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from exceptions import QidQuantityMismatchException

PRINT_FILE_TEMPLATE = ('UAC', 'QUESTIONNAIRE_ID', 'WALES_UAC', 'WALES_QUESTIONNAIRE_ID', 'TITLE', 'FORENAME', 'SURNAME',
                       'ADDRESS_LINE1', 'ADDRESS_LINE2', 'ADDRESS_LINE3', 'TOWN_NAME', 'POSTCODE', 'PRODUCTPACK_CODE')

PRODUCTPACK_CODE_TO_DESCRIPTION = {
    'D_FD_H1': 'Household Questionnaire pack for England',
    'D_FD_H2': 'Household Questionnaire pack for Wales (English)',
    'D_FD_H2W': 'Household Questionnaire pack for Wales (Welsh)',
    'D_FD_H4': 'Household Questionnaire pack for Northern Ireland (English)',
    'D_FD_HC1': 'Continuation Questionnaire pack for England',
    'D_FD_HC2': 'Continuation Questionnaire pack for Wales (English)',
    'D_FD_HC2W': 'Continuation Questionnaire pack for Wales (Welsh)',
    'D_FD_HC4': 'Continuation Questionnaire pack for Northern Ireland (English)',
    'D_FD_I1': 'Individual Questionnaire pack for England',
    'D_FD_I2': 'Individual Questionnaire pack for Wales (English)',
    'D_FD_I2W': 'Individual Questionnaire pack for Wales (Welsh)',
    'D_FD_I4': 'Individual Questionnaire pack for Northern Ireland (English)',
    'D_CCS_CH1': 'CCS Interviewer Household Questionnaire for England and Wales',
    'D_CCS_CH2W': 'CCS Interviewer Household Questionnaire for Wales (Welsh)',
    'D_CCS_CHP1': 'CCS Postback for England',
    'D_CCS_CHP2W': 'CCS Postback for Wales (English and Welsh)',
    'D_CCS_CCP1': 'CCS Postback Continuation Questionnaire for England & Wales',
    'D_CCS_CCP2W': 'CCS Postback Continuation Questionnaire for Wales (Welsh)',
    'D_CCS_CCE1': 'CCS Interviewer CE Manager for England & Wales (English)',
    'D_CCS_CCE2W': 'CCS Interviewer CE Manager for Wales (Welsh)'
}


def _get_uac_qid_links(engine, questionnaire_type):
    uac_qid_links_query = text("SELECT * FROM casev2.uac_qid_link WHERE SUBSTRING(qid FROM 1 FOR 2)"
                               "= :questionnaire_type AND caze_case_ref IS NULL")

    return engine.execute(uac_qid_links_query, questionnaire_type=questionnaire_type)


def create_db_engine():
    db_port = os.getenv('DB_PORT', '6432')
    db_name = os.getenv('DB_NAME', 'postgres')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_username = os.getenv('DB_USERNAME', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    db_uri = f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'
    return create_engine(db_uri)


def generate_print_files_from_config_file_path(config_file_path: Path, output_file_path: Path) -> List[Path]:
    with open(config_file_path) as config_file:
        return generate_print_files_from_config_file(config_file, output_file_path)


def generate_print_files_from_config_file(config_file, output_file_path: Path) -> List[Path]:
    config_file_reader = csv.DictReader(config_file)
    db_engine = create_db_engine()
    file_paths = []
    for config_row in config_file_reader:
        uac_qid_links = _get_uac_qid_links(db_engine, config_row['Questionnaire type'])
        filename = f'{config_row["Pack code"]}_{datetime.utcnow().strftime("%Y-%M-%dT%H-%M-%S")}'
        print_file_path = output_file_path.joinpath(f'{filename}.csv')
        generate_print_file(print_file_path, uac_qid_links, config_row)
        file_paths.append(print_file_path)
        manifest_file_path = output_file_path.joinpath(f'{filename}.manifest')
        generate_manifest_file(manifest_file_path, print_file_path, config_row['Pack code'])
        file_paths.append(manifest_file_path)
    return file_paths


def generate_print_file(print_file_path: Path, uac_qid_links, config):
    with open(print_file_path, 'w') as print_file:
        csv_writer = csv.DictWriter(print_file, fieldnames=PRINT_FILE_TEMPLATE, delimiter='|')
        row_count = 0
        for result_row in uac_qid_links:
            row_count += 1
            print_row = {'UAC': result_row['uac'], 'QUESTIONNAIRE_ID': result_row['qid'],
                         'PRODUCTPACK_CODE': config["Pack code"]}
            csv_writer.writerow(print_row)
        if row_count != int(config["Quantity"]):
            raise QidQuantityMismatchException(f'expected = {config["Quantity"]}, found = {row_count}, '
                                               f'questionnaire type = {config["Questionnaire type"]}')


def generate_manifest_file(manifest_file_path: Path, print_file_path: Path, productpack_code: str):
    manifest = create_manifest(manifest_file_path, print_file_path, productpack_code)
    manifest_file_path.write_text(json.dumps(manifest))


def create_manifest(manifest_file_path: Path, print_file_path: Path, productpack_code: str) -> dict:
    manifest = {
        'schemaVersion': '1',
        'description': PRODUCTPACK_CODE_TO_DESCRIPTION[productpack_code],
        'dataset': 'QM3.1',
        'version': '1',
        'manifestCreated': datetime.utcnow().isoformat(),
        'files': [
            {
                'name': print_file_path.name,
                'relativePath': str(print_file_path.absolute().relative_to(manifest_file_path.absolute().parent)),
                'sourceName': 'ONS_RM',
                'sizeBytes': str(print_file_path.stat().st_size)
            }
        ]
    }
    with open(print_file_path, 'rb') as print_file:
        manifest['files'][0]['md5Sum'] = hashlib.md5(print_file.read()).hexdigest()
    return manifest


def copy_files_to_gcs(file_paths: Collection[Path]):
    client = storage.Client()
    bucket = client.get_bucket(f'{client.project}-print-files')
    for file_path in file_paths:
        bucket.blob(file_path.name).upload_from_filename(filename=str(file_path))
    print(f'All {len(file_paths)} files successfully written to {bucket.name}')


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Generate a print file from a CSV config file specifying questionnaire types and respective '
                    'QID/UAC counts')
    parser.add_argument('config_file_path', help='Path to the CSV config file', type=Path)
    parser.add_argument('output_file_path', help='Directory to write output files', type=Path)
    return parser.parse_args()


def main():
    args = parse_arguments()
    print(args.config_file_path)
    file_paths = generate_print_files_from_config_file_path(args.config_file_path, args.output_file_path)
    copy_files_to_gcs(file_paths)


if __name__ == '__main__':
    main()
