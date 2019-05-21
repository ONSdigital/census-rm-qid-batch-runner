import argparse
import csv
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.sql import text


PRINT_FILE_TEMPLATE = ('UAC', 'QUESTIONNAIRE_ID', 'WALES_UAC', 'WALES_QUESTIONNAIRE_ID', 'ADDRESS_LINE1',
                       'ADDRESS_LINE2', 'ADDRESS_LINE3', 'TOWN_NAME', 'POSTCODE', 'PRODUCTPACK_CODE')


class QidQuantityMismatchException(Exception):
    pass


def _get_uac_qid_links(engine, questionnaire_type):
    uac_qid_links_query = text("SELECT * FROM casev2.uac_qid_link WHERE SUBSTRING(qid from 1 for 2)"
                               "= :questionnaire_type and caze_case_ref is null")

    return engine.execute(uac_qid_links_query, questionnaire_type=questionnaire_type)


def initialise_db():
    return create_engine('postgresql://postgres:postgres@localhost:6432/postgres')


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


if __name__ == '__main__':
    main()
