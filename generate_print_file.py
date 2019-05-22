import argparse
import csv
import os
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from google.cloud import storage


PRINT_FILE_TEMPLATE = ('UAC', 'QUESTIONNAIRE_ID', 'WALES_UAC', 'WALES_QUESTIONNAIRE_ID', 'ADDRESS_LINE1',
                       'ADDRESS_LINE2', 'ADDRESS_LINE3', 'TOWN_NAME', 'POSTCODE', 'PRODUCTPACK_CODE')


class QidQuantityMismatchException(Exception):
    pass


def _get_uac_qid_links(engine, questionnaire_type):
    uac_qid_links_query = text("SELECT * FROM casev2.uac_qid_link WHERE SUBSTRING(qid from 1 for 2)"
                               "= :questionnaire_type and caze_case_ref is null")

    return engine.execute(uac_qid_links_query, questionnaire_type=questionnaire_type)


def initialise_db():
    db_port=os.getenv('db_port', "NoValue")
    db_name=os.getenv('db_name', 'NoValue')
    db_host=os.getenv('db_host', 'NoValue')
    db_password_file = open("/root/.db-credentials/password", "r")
    for line in db_password_file:
        db_password = line
    db_username_file = open("/root/.db-credentials/username", "r")
    for line in db_username_file:
        db_username = line
    conn_str = f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'
    print(conn_str)
    return create_engine(conn_str)


def generate_printfile_from_config_file_path(config_file_path: Path, output_file_path: Path):
    with open(config_file_path) as config_file:
        generate_printfile_from_config_file(config_file, output_file_path)


def generate_printfile_from_config_file(config_file, output_file_path: Path):
    config_file_reader = csv.DictReader(config_file)
    engine = initialise_db()
    for config_row in config_file_reader:
        results = _get_uac_qid_links(engine, config_row['Questionnaire type'])
        filename = f'{config_row["Pack code"]}_{datetime.utcnow().strftime("%Y-%M-%dT%H-%M-%S")}.csv'
        with open(output_file_path.joinpath(filename), 'w') as printfile:
            csv_writer = csv.DictWriter(printfile, fieldnames=PRINT_FILE_TEMPLATE, delimiter='|')
            row_count = 0
            for result_row in results:
                row_count += 1
                print_row = {'UAC': result_row['uac'], 'QUESTIONNAIRE_ID': result_row['qid'],
                             'PRODUCTPACK_CODE': config_row["Pack code"]}
                csv_writer.writerow(print_row)
            if row_count != int(config_row["Quantity"]):
                raise QidQuantityMismatchException(f'expected = {config_row["Quantity"]}, found = {row_count}, '
                                                   f'questionnaire type = {config_row["Questionnaire type"]}')


def copy_printfiles_to_gcs():
    client = storage.Client()
    bucket = client.create_bucket('print_files')
    print('Bucket {} created'.format(bucket.name))
    print_files_dir = '/app/print_files'
    files = os.listdir(print_files_dir)
    for file in files:
        blob2 = bucket.blob(file)
        file_path = f'{print_files_dir}/{file}'
        blob2.upload_from_filename(filename=file_path)


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
    generate_printfile_from_config_file_path(args.config_file_path, args.output_file_path)
    copy_printfiles_to_gcs()


if __name__ == '__main__':
    main()
