import argparse
import functools
import uuid
from pathlib import Path
from typing import Collection

from google.cloud import storage

from rabbit_context import RabbitContext


def start_listening_to_rabbit_queue(queue, on_message_callback, timeout=30):
    rabbit = RabbitContext(queue_name=queue)
    connection = rabbit.open_connection()

    connection.call_later(
        delay=timeout,
        callback=functools.partial(_timeout_callback, rabbit))
    rabbit.channel.basic_consume(
        queue=queue,
        on_message_callback=on_message_callback)
    rabbit.channel.start_consuming()


def _timeout_callback(rabbit):
    print('Message queue appears to be drained')
    rabbit.close_connection()


def dump_messages(queue_name, output_file_path):
    file_paths = []
    start_listening_to_rabbit_queue(queue_name,
                                    functools.partial(_callback, output_file_path=output_file_path, file_paths=file_paths))
    return file_paths


def _callback(ch, method, _properties, body, output_file_path, file_paths):
    output_file = output_file_path.joinpath(f'{str(uuid.uuid4())}.json')
    file_paths.append(output_file)
    dump_message_to_file(output_file,  body)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def dump_message_to_file(print_file_path: Path, message_body):
    with open(print_file_path, 'w') as print_file:
        print_file.write(message_body.decode("utf-8"));


def copy_files_to_gcs(file_paths: Collection[Path], queue_name):
    client = storage.Client()
    bucket = client.get_bucket(f'{client.project}-{queue_name}-queue-dump-files')
    print(f'Copying files to GCS bucket {bucket.name}')
    for file_path in file_paths:
        bucket.blob(file_path.name).upload_from_filename(filename=str(file_path))
    print(f'All {len(file_paths)} files successfully written to {bucket.name}')


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Dump the contents of a Rabbit queue to individual message files in a directory')
    parser.add_argument('queue_name', help='Name of the Rabbit queue to consume messages from', type=str)
    parser.add_argument('output_file_path', help='Directory to write output files', type=Path)
    parser.add_argument('--no-gcs', help="Don't copy the files to a GCS bucket", required=False, action='store_true')
    return parser.parse_args()


def main():
    args = parse_arguments()
    file_paths = dump_messages(args.queue_name, args.output_file_path)
    if not args.no_gcs:
        copy_files_to_gcs(file_paths, args.queue_name)


if __name__ == '__main__':
    main()
