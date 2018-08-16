import datetime
from base64 import b64encode
from hashlib import sha256
import hmac

from django.conf import settings


def create_sha256_signature(key, message):
    """
    Signs an HMAC SHA-256 signature to a message with Base 64
    encoding. This is required by CyberSource.
    """
    digest = hmac.new(
        key.encode(),
        msg=message.encode(),
        digestmod=sha256,
    ).digest()
    return b64encode(digest).decode()


def sign_fields_to_context(fields, context):
    """
    Builds the list of file names and data to sign, and created the
    signature required by CyberSource.
    """
    fields['device_fingerprint_id'] = 'C0F803ADD371A99929B8AD40A439792F'
    fields['signed_date_time'] = str(datetime.datetime.utcnow().isoformat(timespec='seconds')) + 'Z'
    signed_field_names = []
    data_to_sign = []
    for key, value in fields.items():
        signed_field_names.append(key)
        data_to_sign.append(f'{key}={value}')

    print(','.join(data_to_sign))

    context['fields'] = fields
    context['signed_field_names'] = ','.join(signed_field_names)
    context['signature'] = create_sha256_signature(
        settings.CYBERSOURCE_SECRET_KEY,
        ','.join(data_to_sign),
    )
    context['url'] = settings.CYBERSOURCE_URL

    return context
