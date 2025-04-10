from sm3lib import SM3_len_ex_ak as __sm3_iter
from gmssl.sm3 import sm3_hash
from gmssl.func import bytes_to_list
from base64 import b16encode


def b16(text: bytes):
    return b16encode(text)


def sm3_iter(num_block, IV, suffix: bytes):
    return __sm3_iter(num_block, IV, b16(suffix).decode())


def sm3(text: bytes):
    return sm3_hash(bytes_to_list(text))


def sm3_padding(text: str):
    text_length = len(text) * 8
    text += b"\x80"
    k = 448 - (text_length + 1) % 512
    text += b"\x00" * (k // 8)
    text += text_length.to_bytes(8, byteorder="big")
    return text


def sm3_suffix(text: bytes, suffix: bytes):
    return sm3_padding(text) + suffix


if __name__ == "__main__":

    # def suffix(text, num_block, add):
    #     pass

    # sign = sm3(secret.pwd.payload)        # 8f8d8e8ffa9ea490f5801af56179bc36.penguins.tomo0.GO -> 4db073f3e0ccdb6b42be7e7dfb4e5fb7beff7b85ea483768c6051950dd831d11
    # payload = user.org                    # tomo0.GO
    # token format: b64(payload).b64(sign)  # b64(tomo0.GO).b64(8f8d8e8ffa9ea490f5801af56179bc36.penguins.tomo0.GO)

    text = b"8f8d8e8ffa9ea490f5801af56179bc36.penguins.tomo0.GO"
    sign = sm3(text)
    suffix = b".CRYCRY"

    print(sign)
    print(b16(text))
    new_text = sm3_suffix(text, suffix)
    print(new_text)
    print(b16(new_text))
    print(sm3(new_text))
    print(sm3_iter(1, sign, suffix))
    # code.interact(local=locals())
