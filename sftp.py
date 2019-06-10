import os

import paramiko


class SftpUtility:
    def __init__(self):
        self.sftp_directory = os.getenv('SFTP_DIR')
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(hostname=os.getenv('SFTP_HOST', 'sftp'),
                                port=int(os.getenv('SFTP_PORT', 22)),
                                username=os.getenv('SFTP_USERNAME'),
                                key_filename=os.getenv('SFTP_KEY_FILENAME'),
                                passphrase=os.getenv('SFTP_PASSPHRASE'),
                                look_for_keys=False,
                                timeout=120)

    def __enter__(self):
        self._sftp_client = self.ssh_client.open_sftp()
        return self

    def __exit__(self, *_):
        self.ssh_client.close()

    def put_file(self, local_path, filename):
        self._sftp_client.put(local_path, f'{self.sftp_directory}/{filename}')
