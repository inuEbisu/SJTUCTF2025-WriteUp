import time
import hashlib
import requests
import random
import string
from serv import AESCryptService

def generate_data():
    current_ts = int(time.time())
    rounded_ts = (current_ts // 600 + 1) * 600
    current_ts = rounded_ts
    plaintext = f"Give me! It's MyFLAG!!!!!{rounded_ts}"
    print(len(plaintext))
    print(current_ts, rounded_ts, len(plaintext))

    aes = AESCryptService()
    data_hex = aes.encrypt(plaintext)
    return data_hex, current_ts, rounded_ts

def find_code(data_hex, ts):
    prefix = data_hex + str(ts)
    while True:
        # Just a PoW
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        s = prefix + code
        hash_digest = hashlib.md5(s.encode()).hexdigest()
        if hash_digest.startswith('00000'):
            return code

def main():
    # Generate data and timestamp
    data_hex, current_ts, rounded_ts = generate_data()
    print(f"Data: {data_hex}")
    print(f"Timestamp: {current_ts}")
    print(f"Rounded: {rounded_ts}")
    # Find valid code
    code = find_code(data_hex, rounded_ts)
    print(f"Code found: {code}")

    # Send POST request to the server
    url = "http://6bfm9v272mqfp7gw.instance.penguin.0ops.sjtu.cn:18080/flag"
    form_data = {
        "data": data_hex,
        "code": code,
        "timestamp": str(rounded_ts)
    }
    while True:
        time.sleep(2)
        response = requests.post(url, data=form_data)
        print("Response from server:")
        print(response.status_code)
        print(response.json())

if __name__ == "__main__":
    main()