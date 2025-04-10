from funcs import sm3_iter
from base64 import b64encode
from app import b64_encode, b64_decode
from client import APIClient


def get_padding(text_length: int):
    text = b""
    text_length = text_length * 8
    text += b"\x80"
    k = 448 - (text_length + 1) % 512
    text += b"\x00" * (k // 8)
    text += text_length.to_bytes(8, byteorder="big")
    return text


def payload_padding(payload: bytes, secret_length: int, suffix: bytes):
    return (
        payload + get_padding(secret_length + len(".penguins.") + len(payload)) + suffix
    )


def generate_token(payload: bytes, signature: bytes):
    lst = [b64encode(payload).decode(), b64_encode(signature)]
    return ".".join(lst)


SUFFIX = b".CRYCRY"

client = APIClient()
client.login()
token = client.token
go_note = client.get_note()

payload, signature = token.split(".")
payload = b64_decode(payload)
signature = b64_decode(signature)

for __secret_len in range(20, 41, 2):
    new_payload = payload_padding(payload.encode(), __secret_len, SUFFIX)
    new_signature = sm3_iter(num_block=1, IV=signature, suffix=SUFFIX)
    new_token = generate_token(new_payload, new_signature)

    new_client = APIClient()
    client.login()
    client.token = new_token
    try:
        note = client.get_note()
    except Exception as e:
        pass
    else:
        print(note)
