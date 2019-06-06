import os

import pgpy

from exceptions import EncryptionFailedException


def pgp_encrypt_message(message):
    # A key can be loaded from a file, like so:
    our_key, _ = pgpy.PGPKey.from_file(os.getenv('OUR_PUBLIC_KEY_PATH'))
    other_key, _ = pgpy.PGPKey.from_file(os.getenv('OTHER_PUBLIC_KEY_PATH'))

    # this creates a standard message from text
    # it will also be compressed, by default with ZIP DEFLATE, unless otherwise specified
    text_message = pgpy.PGPMessage.new(message)

    cipher = pgpy.constants.SymmetricKeyAlgorithm.AES256
    sessionkey = cipher.gen_key()

    # encrypt the message to multiple recipients
    encrypted_message_v1 = our_key.encrypt(text_message, cipher=cipher, sessionkey=sessionkey)
    encrypted_message_v2 = other_key.encrypt(encrypted_message_v1, cipher=cipher, sessionkey=sessionkey)

    # do at least this as soon as possible after encrypting to the final recipient
    del sessionkey

    if encrypted_message_v2.is_encrypted:
        return str(encrypted_message_v2)
    raise EncryptionFailedException
