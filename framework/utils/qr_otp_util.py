import base64
import re
from io import BytesIO

import cv2
import pyotp
from PIL import Image
from pyzbar.pyzbar import decode

from framework.consts.project import RESOURCES_IMAGES_DIR

qr_path = RESOURCES_IMAGES_DIR
qr_filename = 'qr_code.png'


def convert_base64_to_image(base64_string, filename=''):
    filename = filename or qr_filename
    qr_file_path = f"{qr_path}/{filename}"
    with open(qr_file_path, 'wb') as _:
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        image.save(qr_file_path)
    return qr_file_path


def convert_image_to_base64(filename):
    with open(filename, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string


def extract_secret_key_from_qr_image(image_path):
    img = cv2.imread(image_path)
    decoded_objects = decode(img)
    obj_item = [obj for obj in decoded_objects if obj.type == 'QRCODE'][0]
    qr_data = obj_item.data.decode('utf-8')
    secret_str = re.findall("secret=[^&]+", qr_data)[0]
    secret_key = secret_str.split('=')[1]
    return secret_key


def gen_otp(secret_key):
    totp = pyotp.TOTP(secret_key)
    otp = totp.now()
    return otp


def get_otp_from_qr_code(qr_base64):
    image_string = qr_base64.replace('data:image/png;base64,', '')
    image_path = convert_base64_to_image(image_string)
    secret_key = extract_secret_key_from_qr_image(image_path)
    otp = gen_otp(secret_key)
    return otp
