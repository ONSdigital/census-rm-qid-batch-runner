import argparse
import csv
import uuid
from pathlib import Path

from generate_print_files import PRINT_FILE_TEMPLATE, generate_print_files_from_config_file_path


def validate_print_file_data(file_paths):
    manifests = [file_path for file_path in file_paths if file_path.suffix == '.manifest']
    print_files = [file_path for file_path in file_paths if file_path.suffix == '.csv']

    assert len(manifests) == 3, 'Incorrect number of manifest files'

    with open(Path('test_batch.csv')) as batch_config:
        config_file = list(csv.DictReader(batch_config))

    for index, print_file in enumerate(print_files):
        with open(print_file) as print_file_handler:
            print_file_reader = csv.DictReader(print_file_handler, delimiter='|', fieldnames=PRINT_FILE_TEMPLATE)

            row_counter = 0
            for row in print_file_reader:
                row_counter += 1
                assert len(row['UAC']) == 16, 'Incorrect UAC length'
                assert row['PRODUCTPACK_CODE'] == config_file[index]['Pack code'], \
                    'PRODUCTPACK_CODE does not match config'
                assert row['QUESTIONNAIRE_ID'][:2] == config_file[index]['Questionnaire type'], \
                    'QUESTIONNAIRE_ID does not match config'
            assert row_counter == int(config_file[index]['Quantity']), 'Print file row count does not match config'


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch-id', help='UUID for this qid/uac pair batch',
                        type=uuid.UUID, required=True)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    file_paths = generate_print_files_from_config_file_path(Path('test_batch.csv'), Path('print_files'), args.batch_id)
    validate_print_file_data(file_paths)
    print('TESTS PASSED')
