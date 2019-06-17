import argparse
from pathlib import Path

from rabbit_context import RabbitContext


def publish_messages_from_config_file_path(queue_name, source_file_path, destination_file_path):
    with RabbitContext(queue_name=queue_name) as rabbit:
        for file_path in source_file_path.rglob('*.json'):
            rabbit.publish_message(file_path.read_text(), 'application/json')
            file_path.replace(destination_file_path.joinpath(file_path.name))


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Publish each file in a directory as a message to a rabbit queue')
    parser.add_argument('queue_name', help='Name of queue to publish to', type=str)
    parser.add_argument('source_file_path', help='Directory to read input files from', type=Path)
    parser.add_argument('destination_file_path', help='Directory to move published input files to', type=Path)
    return parser.parse_args()


def main():
    args = parse_arguments()
    publish_messages_from_config_file_path(args.queue_name, args.source_file_path, args.destination_file_path)


if __name__ == '__main__':
    main()
