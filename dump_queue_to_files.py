import argparse
import functools
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from google.cloud import storage

from rabbit_context import RabbitContext

queue_quantity = 0


def start_listening_to_rabbit_queue(queue, on_message_callback):
    rabbit = RabbitContext(queue_name=queue)
    rabbit.open_connection()

    rabbit.channel.basic_consume(
        queue=queue,
        on_message_callback=on_message_callback)
    rabbit.channel.start_consuming()


def dump_messages(queue_name, output_file_path):
    directory_path = output_file_path.joinpath(f'{queue_name}_{datetime.utcnow().strftime("%Y-%M-%dT%H-%M-%S")}')
    directory_path.mkdir()
    print(f'Writing messages to path: {directory_path.stem}')
    print(f'Started processing Rabbit messages on queue {queue_name}')
    start_listening_to_rabbit_queue(queue_name,
                                    functools.partial(_rabbit_message_received_callback,
                                                      output_file_path=output_file_path))
    return directory_path


def _rabbit_message_received_callback(ch, method, _properties, body, output_file_path):
    output_file = output_file_path.joinpath(f'{str(uuid.uuid4())}.json')
    output_file.write_text(body.decode("utf-8"))
    ch.basic_ack(delivery_tag=method.delivery_tag)

    global queue_quantity
    queue_quantity -= 1

    if queue_quantity % 500 == 0:
        print(f'{queue_quantity} messages remaining to be written to files')

    if queue_quantity == 0:
        ch.stop_consuming()


def copy_file_to_gcs(file_path: Path):
    client = storage.Client()
    bucket = client.get_bucket(f'{client.project}-queue-dump-files')
    print(f'Copying files to GCS bucket {bucket.name}')
    bucket.blob(f'{file_path.name}').upload_from_filename(filename=str(file_path))
    print(f'All files successfully written to {bucket.name}')


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Dump the contents of a Rabbit queue to individual message files in a directory')
    parser.add_argument('queue_name', help='Name of the Rabbit queue to consume messages from', type=str)
    parser.add_argument('queue_quantity', help='Number of Rabbit messages to consume', type=int)
    parser.add_argument('output_file_path', help='Directory to write output files', type=Path)
    parser.add_argument('--no-gcs', help="Don't copy the files to a GCS bucket", required=False, action='store_true')
    return parser.parse_args()


def main():
    args = parse_arguments()
    global queue_quantity
    queue_quantity = args.queue_quantity
    output_directory = dump_messages(args.queue_name, args.output_file_path)
    if not args.no_gcs:
        print(f'All {args.queue_quantity} messages received. Zipping up message files')
        output_archive = Path(shutil.make_archive(str(output_directory), 'zip', str(output_directory)))
        copy_file_to_gcs(output_archive)


if __name__ == '__main__':
    main()
