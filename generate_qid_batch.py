import argparse
import csv
import json
from pathlib import Path

from rabbit_context import RabbitContext


def generate_messages_from_config_file_path(config_file_path: Path):
    with open(config_file_path) as config_file:
        generate_messages_from_config_file(config_file)


def generate_messages_from_config_file(config_file):
    config_file_reader = csv.DictReader(config_file)
    with RabbitContext() as rabbit:
        for row in config_file_reader:
            message_count = int(row['Quantity'])
            message_json = create_message_json(row['Questionnaire type'])
            print(f'Queueing {message_count} questionnaire type {row["Questionnaire type"]}')
            for _ in range(message_count):
                rabbit.publish_message(message_json, 'application/json')


def create_message_json(questionnaire_type):
    return json.dumps({'questionnaireType': questionnaire_type})


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Generate unaddressed QID/UAC request messages from a CSV config file'
                    ' specifying questionnaire types and respective counts')
    parser.add_argument('config_file_path', help='Path to the CSV config file', type=Path)
    return parser.parse_args()


def main():
    args = parse_arguments()
    generate_messages_from_config_file_path(args.config_file_path)


if __name__ == '__main__':
    main()
