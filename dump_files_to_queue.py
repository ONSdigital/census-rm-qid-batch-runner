import argparse
from pathlib import Path

from rabbit_context import RabbitContext


def publish_messages_from_json_file_path(queue_name: str, source_file_path: Path, destination_file_path: Path):
    """
    NB: this exists to support the single (JSON) file model and should not be used with the new style (dump) files
    """
    with RabbitContext(queue_name=queue_name) as rabbit:
        for file_path in source_file_path.rglob('*.json'):
            rabbit.publish_message(file_path.read_text(), 'application/json')
            file_path.replace(destination_file_path.joinpath(file_path.name))


def publish_messages_from_dump_files(queue_name: str, source_file_path: Path, destination_file_path: Path):
    with RabbitContext(queue_name=queue_name) as rabbit:
        for file_path in source_file_path.rglob('*.dump'):
            for json_message in file_path.open():
                rabbit.publish_message(json_message, 'application/json')
            file_path.replace(destination_file_path.joinpath(file_path.name))


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Publish each file in a directory as a message to a rabbit queue')
    parser.add_argument('queue_name', help='Name of queue to publish to', type=str)
    parser.add_argument('source_file_path', help='Directory to read input files from', type=Path)
    parser.add_argument('destination_file_path', help='Directory to move published input files to', type=Path)
    parser.add_argument('--separate-files', help="Each message has its own (JSON) file [LEGACY]", required=False,
                        action='store_true')
    return parser.parse_args()


def main():
    args = parse_arguments()
    if args.separate_files:
        publish_messages_from_json_file_path(args.queue_name, args.source_file_path, args.destination_file_path)
    else:
        publish_messages_from_dump_files(args.queue_name, args.source_file_path, args.destination_file_path)


if __name__ == '__main__':
    main()
