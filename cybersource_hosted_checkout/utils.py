import hmac
from hashlib import sha256
from base64 import b64encode


def create_sha256_signature(key, message):
    digest = hmac.new(
        key.encode(),
        msg=message.encode(),
        digestmod=sha256,
    ).digest()
    return b64encode(digest).decode()
