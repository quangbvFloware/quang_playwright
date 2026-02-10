import base64
import hashlib
import random

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


def hash_md5(value: str):
    return hashlib.md5(value.encode()).hexdigest()


def encrypt_rsa_base64(raw_msg, keypath):
    if isinstance(keypath, bytes) or isinstance(keypath, str):
        publickey = keypath
    else:
        with open(keypath, "rb") as f:
            publickey = f.read()

    pubKeyObj = RSA.importKey(publickey)
    cipher = PKCS1_v1_5.new(pubKeyObj)

    if isinstance(raw_msg, bytes):
        msg = raw_msg
    else:
        msg = raw_msg.encode("utf-8")
    emsg = cipher.encrypt(msg)
    return base64.b64encode(emsg).decode("utf-8")


def decrypt_rsa_base64(raw_msg, keypath):
    if isinstance(keypath, bytes) or isinstance(keypath, str):
        privatekey = keypath
    else:
        with open(keypath, "rb") as f:
            privatekey = f.read()

    priKeyObj = RSA.importKey(privatekey)
    cipher = PKCS1_v1_5.new(priKeyObj)

    if isinstance(raw_msg, bytes):
        msg = raw_msg.decode("utf-8")
    else:
        msg = base64.b64decode(raw_msg)
    emsg = cipher.decrypt(msg, sentinel=random.random())
    return emsg.decode("utf-8")


def encrypt_photo_base64(filepath):
    with open(filepath, "rb") as img_file:
        raw_msg = base64.b64encode(img_file.read())
    return raw_msg.decode("utf-8")


def encode_base64(text: str) -> str:
    """Mã hóa chuỗi sang Base64."""
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    return base64.b64encode(text.encode("utf-8")).decode("utf-8")


def decode_base64(encoded: str) -> str:
    """Giải mã chuỗi Base64."""
    if not isinstance(encoded, str):
        raise TypeError("Input must be a string")
    return base64.b64decode(encoded.encode("utf-8")).decode("utf-8")
